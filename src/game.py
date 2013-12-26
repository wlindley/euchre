class GameException(Exception):
	pass

class InvalidPlayerException(GameException):
	pass

class GameRuleException(GameException):
	pass

class GameStateException(GameException):
	pass

class Player(object):
	instance = None
	@classmethod
	def getInstance(cls, playerId):
		if None != cls.instance:
			return cls.instance
		return Player(playerId)

	def __init__(self, playerId):
		self.playerId = playerId

	def __eq__(self, other):
		if not other:
			return False
		if not isinstance(other, Player):
			return other.__eq__(self)
		return self.playerId == other.playerId

	def __repr__(self):
		return 'Player("%s")' % self.playerId

class TurnTracker(object):
	instance = None
	@classmethod
	def getInstance(cls, players):
		if None != cls.instance:
			return cls.instance
		return TurnTracker(players)

	def __init__(self, players):
		self._players = players
		self._currentIndex = 0
		self._allTurnCount = 0
		self.reset()

	def getCurrentPlayerId(self):
		return self._players[self._currentIndex].playerId

	def advanceTurn(self):
		if (len(self._players) - 1) == self._currentIndex:
			self._allTurnCount += 1
		self._currentIndex = (self._currentIndex + 1) % len(self._players)

	def setTurnByPlayerId(self, playerId):
		for i in range(len(self._players)):
			if playerId == self._players[i].playerId:
				self._currentIndex = i
				return

	def getAllTurnCount(self):
		return self._allTurnCount

	def reset(self):
		self._currentIndex = 0
		self._allTurnCount = 0
