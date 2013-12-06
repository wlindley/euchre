from google.appengine.ext import ndb

CURRENT_GAME_MODEL_VERSION = 3

class RootModel(ndb.Model):
	pass

class PlayerModel(ndb.Model):
	playerId = ndb.StringProperty(required=True)

class GameModel(ndb.Model):
	serializedGame = ndb.JsonProperty(default='')
	playerId = ndb.StringProperty(repeated=True)
	teams = ndb.JsonProperty()
	version = ndb.IntegerProperty(default=1)
	readyToRemove = ndb.StringProperty(repeated=True)

MatchmakingTicketRootKey = ndb.Key(RootModel, "matchmaking_tickets")

class MatchmakingTicketModel(ndb.Model):
	playerId = ndb.StringProperty(required=True)
	lookingForMatch = ndb.BooleanProperty(default=True)
	searchStartTime = ndb.DateTimeProperty(auto_now=True)

class GameModelFactory(object):
	instance = None
	@classmethod
	def getInstance(cls):
		if None != cls.instance:
			return cls.instance
		return GameModelFactory()

	def create(self):
		return GameModel(version=CURRENT_GAME_MODEL_VERSION)

class GameModelFinder(object):
	instance = None
	@classmethod
	def getInstance(cls):
		if None != cls.instance:
			return cls.instance
		return GameModelFinder()

	FETCH_SIZE = 50

	def getGamesForPlayerId(self, playerId):
		query = self._getQuery(playerId)
		models = query.fetch(GameModelFinder.FETCH_SIZE)
		return models

	def _getQuery(self, playerId):
		return GameModel.query(GameModel.playerId == playerId)

	def getGameByGameId(self, gameId):
		return self._getKeyByUrl(gameId).get()

	def _getGameIdQuery(self, gameId):
		return GameModel.query(GameModel.gameId == gameId)

	def _getKeyByUrl(self, urlsafe):
		return ndb.Key(urlsafe=urlsafe)

	def deleteGame(self, gameId):
		key = self._getKeyByUrl(gameId)
		if None == key:
			return False
		key.delete()
		return True

class MatchmakingTicketFinder(object):
	instance = None
	@classmethod
	def getInstance(cls):
		if None != cls.instance:
			return cls.instance
		return MatchmakingTicketFinder()

	def isPlayerInQueue(self, playerId):
		ticketModel = self._getModel(playerId)
		if None == ticketModel:
			return False
		return ticketModel.lookingForMatch

	def addPlayerToQueue(self, playerId):
		ticketModel = self._getModel(playerId)
		if None == ticketModel:
			ticketModel = MatchmakingTicketModel(key=self._getKey(playerId))
			ticketModel.playerId = playerId
			ticketModel.lookingForMatch = False
		if not ticketModel.lookingForMatch:
			ticketModel.lookingForMatch = True
			ticketModel.put()

	def getMatchmakingGroup(self, numPlayers):
		models = self._getQuery().fetch(3)
		return [m.playerId for m in models]

	def _getKey(self, playerId):
		return ndb.Key(RootModel, "matchmaking_tickets", MatchmakingTicketModel, "matchmaking_ticket_" + playerId)

	def _getModel(self, playerId):
		return self._getKey(playerId).get()

	def _getQuery(self):
		return MatchmakingTicketModel.query(MatchmakingTicketModel.lookingForMatch == True, ancestor=MatchmakingTicketRootKey).order(-MatchmakingTicketModel.searchStartTime)