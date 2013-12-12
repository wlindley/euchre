from abc import ABCMeta
from abc import abstractmethod
import json
import logging
import random
import util
import game
import euchre
import serializer
import model
import retriever
import filter
import social

logging.getLogger().setLevel(logging.DEBUG)

MAX_TEAM_SIZE = 2

class ExecutableFactory(object):
	instance = None
	@classmethod
	def getInstance(cls, requestDataAccessor, responseWriter, session):
		if None != cls.instance:
			return cls.instance
		return ExecutableFactory(requestDataAccessor, responseWriter, session)

	def __init__(self, requestDataAccessor, responseWriter, session):
		self._requestDataAccessor = requestDataAccessor
		self._responseWriter = responseWriter
		self._session = session
		self._executables = {
			"createGame" : CreateGameExecutable,
			"listGames" : ListGamesExecutable,
			"getBasicGameData" : GetBasicGameDataExecutable,
			"addPlayer" : AddPlayerExecutable,
			"getGameData" : GetGameDataExecutable,
			"selectTrump" : SelectTrumpExecutable,
			"playCard" : PlayCardExecutable,
			"discard" : DiscardExecutable,
			"getName" : GetNameExecutable,
			"dismissCompletedGame" : RemoveCompletedGameExecutable,
			"matchmake" : MatchmakingExecutable,
			"getMatchmakingStatus" : GetMatchmakingStatusExecutable
		}

	def createExecutable(self):
		action = self._requestDataAccessor.get("action")
		if action in self._executables:
			return self._executables[action].getInstance(self._requestDataAccessor, self._responseWriter, self._session)
		return DefaultExecutable.getInstance(self._requestDataAccessor, self._responseWriter, self._session)

class AddPlayerStrategy(object):
	instance = None
	@classmethod
	def getInstance(cls):
		if None != cls.instance:
			return cls.instance
		return AddPlayerStrategy(serializer.GameSerializer.getInstance())

	def __init__(self, gameSerializer):
		self._gameSerializer = gameSerializer

	def addPlayerToGame(self, playerId, teamId, gameModel):
		if None == gameModel.teams or 0 >= len(gameModel.teams):
			gameModel.teams = json.dumps([[], []])
		teamInfo = json.loads(gameModel.teams)
		if MAX_TEAM_SIZE <= len(teamInfo[teamId]):
			logging.info("Player %s cannot join game %s because it is already full" % (playerId, gameModel.key.urlsafe()))
			return False
		gameModel.playerId.append(playerId)
		teamInfo[teamId].append(playerId)
		gameModel.teams = json.dumps(teamInfo)
		if MAX_TEAM_SIZE == len(teamInfo[0]) and MAX_TEAM_SIZE == len(teamInfo[1]):
			players = self._buildPlayersFromTeams(teamInfo)
			gameObj = euchre.Game.getInstance(players, teamInfo)
			gameObj.startGame()
			gameModel.serializedGame = self._gameSerializer.serialize(gameObj)
		return True

	def _buildPlayersFromTeams(self, teams):
		firstTeam = random.randint(0, 1)
		teamFirstIndeces = [random.randint(0, 1), random.randint(0, 1)]
		players = []
		for i in range(MAX_TEAM_SIZE * 2):
			currentTeam = (firstTeam + (i % 2)) % 2
			currentIndex = (teamFirstIndeces[currentTeam] + int(i / 2)) % 2
			players.append(game.Player(teams[currentTeam][currentIndex]))
		return players

class AbstractExecutable(object):
	__metaclass__ = ABCMeta

	def __init__(self, requestDataAccessor, responseWriter, session, *args, **kwargs):
		self._requestDataAccessor = requestDataAccessor
		self._responseWriter = responseWriter
		self._session = session

	@abstractmethod
	def execute(self, *args, **kwargs):
		return None

	def _writeResponse(self, response):
		self._responseWriter.write(json.dumps(response, sort_keys=True))

class FacebookUserExecutable(AbstractExecutable):
	def __init__(self, requestDataAccessor, responseWriter, session, facebook):
		super(FacebookUserExecutable, self).__init__(requestDataAccessor, responseWriter, session)
		self._facebook = facebook

	def getSignedInFacebookUser(self):
		return self._facebook.getUser("me")

class CreateGameExecutable(FacebookUserExecutable):
	instance = None
	@classmethod
	def getInstance(cls, requestDataAccessor, responseWriter, session):
		if None != cls.instance:
			return cls.instance
		return CreateGameExecutable(requestDataAccessor, responseWriter, session, model.GameModelFactory.getInstance(), social.Facebook.getInstance(requestDataAccessor, session), AddPlayerStrategy.getInstance())

	def __init__(self, requestDataAccessor, responseWriter, session, gameModelFactory, facebook, addPlayerStrategy):
		super(CreateGameExecutable, self).__init__(requestDataAccessor, responseWriter, session, facebook)
		self._gameModelFactory = gameModelFactory
		self._addPlayerStrategy = addPlayerStrategy

	def execute(self):
		playerId = self.getSignedInFacebookUser().getId()
		team = int(self._requestDataAccessor.get("team"))
		if 1 < team or 0 > team:
			self._writeResponse({"success" : False})
			return
		gameModel = self._gameModelFactory.create()
		self._addPlayerStrategy.addPlayerToGame(playerId, team, gameModel)
		key = gameModel.put()
		self._writeResponse({"success" : True, "gameId" : key.urlsafe()})

class ListGamesExecutable(FacebookUserExecutable):
	instance = None
	@classmethod
	def getInstance(cls, requestDataAccessor, responseWriter, session):
		if None != cls.instance:
			return cls.instance
		return ListGamesExecutable(requestDataAccessor, responseWriter, session, model.GameModelFinder.getInstance(), serializer.GameSerializer.getInstance(), retriever.TurnRetriever.getInstance(), retriever.GameStatusRetriever.getInstance(euchre.WINNING_SCORE), social.Facebook.getInstance(requestDataAccessor, session))

	def __init__(self, requestDataAccessor, responseWriter, session, gameModelFinder, gameSerializer, turnRetriever, gameStatusRetriever, facebook):
		super(ListGamesExecutable, self).__init__(requestDataAccessor, responseWriter, session, facebook)
		self._gameModelFinder = gameModelFinder
		self._gameSerializer = gameSerializer
		self._turnRetriever = turnRetriever
		self._gameStatusRetriever = gameStatusRetriever

	def execute(self):
		playerId = self.getSignedInFacebookUser().getId()
		gameModelFilter = filter.PlayerHasNotRemovedGameModelFilter.getInstance(playerId)
		gameModels = gameModelFilter.filterList(self._gameModelFinder.getGamesForPlayerId(playerId))
		gameDatas = [self._buildGameData(playerId, gameModel) for gameModel in gameModels]
		self._writeResponse({"games" : gameDatas, "success" : True})

	def _buildGameData(self, playerId, gameModel):
		gameData = {
			"gameId" : gameModel.key.urlsafe(),
			"teams" : json.loads(gameModel.teams)
		}
		if None == gameModel.serializedGame or "" == gameModel.serializedGame:
			gameData["status"] = self._gameStatusRetriever.retrieveGameStatus(None)
			gameData["currentPlayerId"] = None
		else:
			gameObj = self._gameSerializer.deserialize(gameModel.serializedGame)
			gameData["status"] = self._gameStatusRetriever.retrieveGameStatus(gameObj)
			gameData["currentPlayerId"] = self._turnRetriever.retrieveTurn(gameObj, playerId)
		return gameData

class GetBasicGameDataExecutable(AbstractExecutable):
	instance = None
	@classmethod
	def getInstance(cls, requestDataAccessor, responseWriter, session):
		if None != cls.instance:
			return cls.instance
		return GetBasicGameDataExecutable(requestDataAccessor, responseWriter, session, model.GameModelFinder.getInstance(), serializer.GameSerializer.getInstance(), retriever.TurnRetriever.getInstance(), retriever.GameStatusRetriever.getInstance(euchre.WINNING_SCORE))

	def __init__(self, requestDataAccessor, responseWriter, session, gameModelFinder, gameSerializer, turnRetriever, gameStatusRetriever):
		super(GetBasicGameDataExecutable, self).__init__(requestDataAccessor, responseWriter, session)
		self._gameModelFinder = gameModelFinder
		self._gameSerializer = gameSerializer
		self._turnRetriever = turnRetriever
		self._gameStatusRetriever = gameStatusRetriever

	def execute(self):
		gameIds = json.loads(self._requestDataAccessor.get("gameIds"))
		logging.info("Getting basic game data for game IDs: %s" % gameIds)
		gameDatas = [self._buildGameData(self._gameModelFinder.getGameByGameId(gameId)) for gameId in gameIds]
		self._writeResponse({"success" : True, "games" : gameDatas})

	def _buildGameData(self, gameModel):
		gameData = {
			"gameId" : gameModel.key.urlsafe(),
			"teams" : json.loads(gameModel.teams)
		}
		if None == gameModel.serializedGame or "" == gameModel.serializedGame:
			gameData["status"] = self._gameStatusRetriever.retrieveGameStatus(None)
			gameData["currentPlayerId"] = None
		else:
			gameObj = self._gameSerializer.deserialize(gameModel.serializedGame)
			gameData["status"] = self._gameStatusRetriever.retrieveGameStatus(gameObj)
			gameData["currentPlayerId"] = self._turnRetriever.retrieveTurn(gameObj, "")
		return gameData

class DefaultExecutable(AbstractExecutable):
	instance = None
	@classmethod
	def getInstance(cls, requestDataAccessor, responseWriter, session):
		if None != cls.instance:
			return cls.instance
		return DefaultExecutable(requestDataAccessor, responseWriter, session)

	def execute(self):
		self._writeResponse({})

class AddPlayerExecutable(FacebookUserExecutable):
	instance = None
	@classmethod
	def getInstance(cls, requestDataAccessor, responseWriter, session):
		if None != cls.instance:
			return cls.instance
		return AddPlayerExecutable(requestDataAccessor, responseWriter, session, model.GameModelFinder.getInstance(), social.Facebook.getInstance(requestDataAccessor, session), AddPlayerStrategy.getInstance())

	def __init__(self, requestDataAccessor, responseWriter, session, gameModelFinder, facebook, addPlayerStrategy):
		super(AddPlayerExecutable, self).__init__(requestDataAccessor, responseWriter, session, facebook)
		self._gameModelFinder = gameModelFinder
		self._addPlayerStrategy = addPlayerStrategy

	def execute(self):
		try:
			team = int(self._requestDataAccessor.get("team"))
		except ValueError:
			logging.info("Non-integer team (%s) specified" % self._requestDataAccessor.get("team"))
			self._writeResponse({"success" : False})
			return
		playerId = self.getSignedInFacebookUser().getId()
		gameId = self._requestDataAccessor.get("gameId")
		gameModel = self._gameModelFinder.getGameByGameId(gameId)
		if None == gameModel or playerId in gameModel.playerId or 1 < team or 0 > team:
			logging.info("No game found for gameId %s or player %s is already in game or invalid team of %s specified" % (gameId, playerId, team))
			self._writeResponse({"success" : False})
			return
		result = self._addPlayerStrategy.addPlayerToGame(playerId, team, gameModel)
		if True == result:
			gameModel.put()
		self._writeResponse({"success" : result})

class GetGameDataExecutable(FacebookUserExecutable):
	instance = None
	@classmethod
	def getInstance(cls, requestDataAccessor, responseWriter, session):
		if None != cls.instance:
			return cls.instance
		return GetGameDataExecutable(requestDataAccessor, responseWriter, session, model.GameModelFinder.getInstance(), serializer.GameSerializer.getInstance(), retriever.TurnRetriever.getInstance(), retriever.HandRetriever.getInstance(), retriever.UpCardRetriever.getInstance(), retriever.DealerRetriever.getInstance(), retriever.GameStatusRetriever.getInstance(euchre.WINNING_SCORE), retriever.LedSuitRetriever.getInstance(), retriever.CurrentTrickRetriever.getInstance(), retriever.TrumpRetriever.getInstance(), retriever.TeamRetriever.getInstance(), retriever.ScoreRetriever.getInstance(), retriever.TrickLeaderRetriever.getInstance(), retriever.PreviousTrickRetriever.getInstance(), social.Facebook.getInstance(requestDataAccessor, session))

	def __init__(self, requestDataAccessor, responseWriter, session, gameModelFinder, gameSerializer, turnRetriever, handRetriever, upCardRetriever, dealerRetriever, gameStatusRetriever, ledSuitRetriever, currentTrickRetriever, trumpRetriever, teamRetriever, scoreRetriever, trickLeaderRetriever, previousTrickRetriever, facebook):
		super(GetGameDataExecutable, self).__init__(requestDataAccessor, responseWriter, session, facebook)
		self._gameModelFinder = gameModelFinder
		self._gameSerializer = gameSerializer
		self._turnRetriever = turnRetriever
		self._handRetriever = handRetriever
		self._upCardRetriever = upCardRetriever
		self._dealerRetriever = dealerRetriever
		self._gameStatusRetriever = gameStatusRetriever
		self._ledSuitRetriever = ledSuitRetriever
		self._currentTrickRetriever = currentTrickRetriever
		self._trumpRetriever = trumpRetriever
		self._teamRetriever = teamRetriever
		self._scoreRetriever = scoreRetriever
		self._trickLeaderRetriever = trickLeaderRetriever
		self._previousTrickRetriever = previousTrickRetriever

	def execute(self):
		playerId = self.getSignedInFacebookUser().getId()
		gameId = self._requestDataAccessor.get("gameId")

		if "" == playerId:
			self._writeResponse({"success" : False})
			return

		gameModel = self._gameModelFinder.getGameByGameId(gameId)

		if None == gameModel or None == gameModel.serializedGame or "" == gameModel.serializedGame:
			self._writeResponse({"success" : False})
			return

		response = {
			"success" : True
		}

		gameObj = self._gameSerializer.deserialize(gameModel.serializedGame)
		response["playerIds"] = gameModel.playerId
		response["gameId"] = gameId
		response["status"] = self._gameStatusRetriever.retrieveGameStatus(gameObj)
		response["teams"] = self._teamRetriever.retrieveTeamLists(gameObj)
		response["scores"] = self._scoreRetriever.retrieveGameScores(gameObj)
		response["round"] = self._getRoundData(gameObj, playerId)
		response["previousTrick"] = self._previousTrickRetriever.retrievePreviousTrick(gameObj);
		self._writeResponse(response)

	def _getRoundData(self, gameObj, playerId):
		roundData = {}
		upCard = self._upCardRetriever.retrieveUpCard(gameObj)
		roundData["tricksTaken"] = self._scoreRetriever.retrieveRoundScores(gameObj)
		roundData["trump"] = self._trumpRetriever.retrieveTrump(gameObj)
		roundData["upCard"] = {"suit" : upCard.suit, "value" : upCard.value} if None != upCard else None
		roundData["dealerId"] = self._dealerRetriever.retrieveDealer(gameObj)
		roundData["hand"] = self._convertHand(self._handRetriever.retrieveHand(playerId, gameObj))
		roundData["currentPlayerId"] = self._turnRetriever.retrieveTurn(gameObj, playerId)
		roundData["currentTrick"] = self._getCurrentTrickData(gameObj)
		return roundData

	def _getCurrentTrickData(self, gameObj):
		trickData = {}
		trickData["ledSuit"] = self._ledSuitRetriever.retrieveLedSuit(gameObj)
		trickData["playedCards"] = self._currentTrickRetriever.retrieveCurrentTrick(gameObj)
		trickData["leaderId"] = self._trickLeaderRetriever.retrieveTrickLeader(gameObj)
		return trickData

	def _convertHand(self, hand):
		return [{"suit" : card.suit, "value" : card.value} for card in hand]

class SelectTrumpExecutable(FacebookUserExecutable):
	instance = None
	@classmethod
	def getInstance(cls, requestDataAccessor, responseWriter, session):
		if None != cls.instance:
			return cls.instance
		return SelectTrumpExecutable(requestDataAccessor, responseWriter, session, model.GameModelFinder.getInstance(), serializer.GameSerializer.getInstance(), retriever.DealerRetriever.getInstance(), retriever.UpCardRetriever.getInstance(), social.Facebook.getInstance(requestDataAccessor, session))

	def __init__(self, requestDataAccessor, responseWriter, session, gameModelFinder, gameSerializer, dealerRetriever, upCardRetriever, facebook):
		super(SelectTrumpExecutable, self).__init__(requestDataAccessor, responseWriter, session, facebook)
		self._gameModelFinder = gameModelFinder
		self._gameSerializer = gameSerializer
		self._dealerRetriever = dealerRetriever
		self._upCardRetriever = upCardRetriever

	def execute(self):
		gameId = self._requestDataAccessor.get("gameId")
		playerId = self.getSignedInFacebookUser().getId()
		suit = self._requestDataAccessor.get("suit")

		if None == gameId or "" == playerId:
			logging.info("Missing game id or player id")
			self._writeResponse({"success" : False})
			return

		if None == suit:
			suit = euchre.SUIT_NONE

		try:
			suit = int(suit)
		except ValueError:
			logging.info("Invalid suit (%s)" % suit)
			self._writeResponse({"success" : False})
			return

		gameModel = self._gameModelFinder.getGameByGameId(gameId)
		if None == gameModel:
			logging.info("Could not find game model for id %s" % gameId)
			self._writeResponse({"success" : False})
			return

		gameObj = self._gameSerializer.deserialize(gameModel.serializedGame)
		dealerPlayer = game.Player.getInstance(self._dealerRetriever.retrieveDealer(gameObj))
		upCard = self._upCardRetriever.retrieveUpCard(gameObj)
		try:
			if euchre.Sequence.STATE_TRUMP_SELECTION == gameObj.getSequenceState() and euchre.SUIT_NONE != suit:
				gameObj.addCardToHand(dealerPlayer, upCard)
			gameObj.selectTrump(game.Player.getInstance(playerId), suit)
		except game.GameException as e:
			logging.info("Error while setting trump (player id: %s, game id: %s, suit: %s): %s" % (playerId, gameId, suit, e))
			self._writeResponse({"success" : False})
			return

		gameModel.serializedGame = self._gameSerializer.serialize(gameObj)
		gameModel.put()

		self._writeResponse({"success" : True})

class PlayCardExecutable(FacebookUserExecutable):
	instance = None
	@classmethod
	def getInstance(cls, requestDataAccessor, responseWriter, session):
		if None != cls.instance:
			return cls.instance
		return PlayCardExecutable(requestDataAccessor, responseWriter, session, model.GameModelFinder.getInstance(), serializer.GameSerializer.getInstance(), social.Facebook.getInstance(requestDataAccessor, session))

	def __init__(self, requestDataAccessor, responseWriter, session, gameModelFinder, gameSerializer, facebook):
		super(PlayCardExecutable, self).__init__(requestDataAccessor, responseWriter, session, facebook)
		self._gameModelFinder = gameModelFinder
		self._gameSerializer = gameSerializer

	def execute(self):
		playerId = self.getSignedInFacebookUser().getId()
		gameId = self._requestDataAccessor.get("gameId")
		cardSuit = self._requestDataAccessor.get("suit")
		cardValue = self._requestDataAccessor.get("value")
		if "" == playerId or None == gameId or None == cardSuit or None == cardValue:
			logging.info("One of the required parameters (player id, game id, card suit, and card value) was not specified")
			self._writeResponse({"success" : False})
			return
		try:
			cardSuit = int(cardSuit)
			cardValue = int(cardValue)
		except ValueError:
			logging.info("Error parsing integer for card suit (%s) or card value (%s)" % (cardSuit, cardValue))
			self._writeResponse({"success" : False})
			return

		gameModel = self._gameModelFinder.getGameByGameId(gameId)
		if None == gameModel:
			logging.info("Could not find game model for game id: %s" % gameId)
			self._writeResponse({"success" : False})
			return
		gameObj = self._gameSerializer.deserialize(gameModel.serializedGame)

		player = game.Player.getInstance(playerId)
		card = euchre.Card.getInstance(cardSuit, cardValue)
		try:
			gameObj.playCard(player, card)
		except game.GameException as e:
			logging.info("Error while player %s tried to play card %s in game %s: %s" % (player, card, gameId, e))
			self._writeResponse({"success" : False})
			return

		gameModel.serializedGame = self._gameSerializer.serialize(gameObj)
		gameModel.put()
		self._writeResponse({"success" : True})

class DiscardExecutable(FacebookUserExecutable):
	instance = None
	@classmethod
	def getInstance(cls, requestDataAccessor, responseWriter, session):
		if None != cls.instance:
			return cls.instance
		return DiscardExecutable(requestDataAccessor, responseWriter, session, model.GameModelFinder.getInstance(), serializer.GameSerializer.getInstance(), social.Facebook.getInstance(requestDataAccessor, session))

	def __init__(self, requestDataAccessor, responseWriter, session, gameModelFinder, gameSerializer, facebook):
		super(DiscardExecutable, self).__init__(requestDataAccessor, responseWriter, session, facebook)
		self._gameModelFinder = gameModelFinder
		self._gameSerializer = gameSerializer

	def execute(self):
		gameId = self._requestDataAccessor.get("gameId")
		playerId = self.getSignedInFacebookUser().getId()
		cardSuit = self._requestDataAccessor.get("suit")
		cardValue = self._requestDataAccessor.get("value")
		if "" == playerId or None == gameId or None == cardSuit or None == cardValue:
			logging.info("One of the required parameters (player id, game id, card suit, and card value) was not specified")
			self._writeResponse({"success" : False})
			return
		try:
			cardSuit = int(cardSuit)
			cardValue = int(cardValue)
		except ValueError:
			logging.info("Error parsing integer for card suit (%s) or card value (%s)" % (cardSuit, cardValue))
			self._writeResponse({"success" : False})
			return

		gameModel = self._gameModelFinder.getGameByGameId(gameId)
		if None == gameModel:
			logging.info("Could not find game model for game id: %s" % gameId)
			self._writeResponse({"success" : False})
			return
		gameObj = self._gameSerializer.deserialize(gameModel.serializedGame)

		player = game.Player.getInstance(playerId)
		card = euchre.Card.getInstance(cardSuit, cardValue)

		try:
			gameObj.discardCard(player, card)
		except game.GameException as e:
			logging.info("Error while player %s tried to play card %s in game %s: %s" % (player, card, gameId, e))
			self._writeResponse({"success" : False})
			return

		gameModel.serializedGame = self._gameSerializer.serialize(gameObj)
		gameModel.put()

		self._writeResponse({"success" : True})

class GetNameExecutable(AbstractExecutable):
	instance = None
	@classmethod
	def getInstance(cls, requestDataAccessor, responseWriter, session):
		if None != cls.instance:
			return cls.instance
		return GetNameExecutable(requestDataAccessor, responseWriter, session)

	def __init__(self, requestDataAccessor, responseWriter, session):
		super(GetNameExecutable, self).__init__(requestDataAccessor, responseWriter, session)

	def execute(self):
		playerId = self._requestDataAccessor.get("playerId")
		if None == playerId:
			self._writeResponse({"success" : False})
		else:
			self._writeResponse({"success" : True, "playerId" : playerId, "name" : "Player " + playerId})

class RemoveCompletedGameExecutable(FacebookUserExecutable):
	instance = None
	@classmethod
	def getInstance(cls, requestDataAccessor, responseWriter, session):
		if None != cls.instance:
			return cls.instance
		return RemoveCompletedGameExecutable(requestDataAccessor, responseWriter, session, model.GameModelFinder.getInstance(), serializer.GameSerializer.getInstance(), social.Facebook.getInstance(requestDataAccessor, session))

	def __init__(self, requestDataAccessor, responseWriter, session, gameModelFinder, gameSerializer, facebook):
		super(RemoveCompletedGameExecutable, self).__init__(requestDataAccessor, responseWriter, session, facebook)
		self._gameModelFinder = gameModelFinder
		self._gameSerializer = gameSerializer

	def execute(self):
		playerId = self.getSignedInFacebookUser().getId()
		gameId = self._requestDataAccessor.get("gameId")

		if None == gameId or None == playerId:
			logging.info("Missing game id (%s) or player id (%s)" % (gameId, playerId))
			self._writeResponse({"success" : False})
			return

		gameModel = self._gameModelFinder.getGameByGameId(gameId)

		if None == gameModel:
			logging.info("Player id %s tried to delete game %s, but that game doesn't exist" % (playerId, gameId))
			self._writeResponse({"success" : False})
			return

		if playerId in gameModel.readyToRemove:
			logging.info("Player id %s tried to delete game %s, but they've already requested deletion" % (playerId, gameId))
			self._writeResponse({"success" : False})
			return

		if not playerId in gameModel.playerId:
			logging.info("Player id %s tried to delete game %s, but they're not part of that game" % (playerId, gameId))
			self._writeResponse({"success" : False})
			return

		game = self._gameSerializer.deserialize(gameModel.serializedGame)

		if not game.isGameComplete():
			logging.info("Player id %s tried to delete game %s, but it's not complete" % (playerId, gameId))
			self._writeResponse({"success" : False})
			return

		gameModel.readyToRemove.append(playerId)

		if len(gameModel.playerId) == len(gameModel.readyToRemove):
			self._gameModelFinder.deleteGame(gameId)
		else:
			gameModel.put()

		self._writeResponse({"success" : True})

class MatchmakingExecutable(FacebookUserExecutable):
	instance = None
	@classmethod
	def getInstance(cls, requestDataAccessor, responseWriter, session):
		if None != cls.instance:
			return cls.instance
		return MatchmakingExecutable(requestDataAccessor, responseWriter, session, social.Facebook.getInstance(requestDataAccessor, session), model.MatchmakingTicketFinder.getInstance(), model.GameModelFactory.getInstance(), AddPlayerStrategy.getInstance())

	def __init__(self, requestDataAccessor, responseWriter, session, facebook, ticketFinder, gameModelFactory, addPlayerStrategy):
		super(MatchmakingExecutable, self).__init__(requestDataAccessor, responseWriter, session, facebook)
		self._ticketFinder = ticketFinder
		self._gameModelFactory = gameModelFactory
		self._addPlayerStrategy = addPlayerStrategy

	ADDITIONAL_PLAYERS = 3

	def execute(self):
		playerId = self.getSignedInFacebookUser().getId()

		if None == playerId or "" == playerId:
			logging.info("Invalid player id when attempting matchmaking")
			self._writeResponse({"success" : False})
			return

		if self._ticketFinder.isPlayerInQueue(playerId):
			logging.info("Attempted matchmaking while player already in queue")
			self._writeResponse({"success" : False})
			return

		players = self._ticketFinder.getMatchmakingGroup(MatchmakingExecutable.ADDITIONAL_PLAYERS)
		if MatchmakingExecutable.ADDITIONAL_PLAYERS == len(players):
			gameModel = self._gameModelFactory.create()
			players += [playerId]
			
			teams = [[], []]
			for pid in players:
				tid = random.randint(0, 1)
				if MAX_TEAM_SIZE <= len(teams[tid]):
					tid = (tid + 1) % 2
				teams[tid].append(pid)
				self._addPlayerStrategy.addPlayerToGame(pid, tid, gameModel)
			gameModel.put()
		else:
			self._ticketFinder.addPlayerToQueue(playerId)

		self._writeResponse({"success" : True})

class GetMatchmakingStatusExecutable(FacebookUserExecutable):
	instance = None
	@classmethod
	def getInstance(cls, requestDataAccessor, responseWriter, session):
		if None != cls.instance:
			return cls.instance
		return GetMatchmakingStatusExecutable(requestDataAccessor, responseWriter, session, social.Facebook.getInstance(requestDataAccessor, session), model.MatchmakingTicketFinder.getInstance())

	def __init__(self, requestDataAccessor, responseWriter, session, facebook, ticketFinder):
		super(GetMatchmakingStatusExecutable, self).__init__(requestDataAccessor, responseWriter, session, facebook)
		self._ticketFinder = ticketFinder

	def execute(self):
		playerId = self.getSignedInFacebookUser().getId()
		if None == playerId or "" == playerId:
			self._writeResponse({"success" : False})
			return

		self._writeResponse({"success" : True, "playerInQueue" : self._ticketFinder.isPlayerInQueue(playerId)})