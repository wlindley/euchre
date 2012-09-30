class InvalidPlayerException(Exception):
	pass

class GameRuleException(Exception):
	pass

class GameStateException(Exception):
	pass

class Player(object):
	def __init__(self, playerId):
		self.playerId = playerId

class TurnTracker(object):
	def __init__(self, players):
		self._players = players
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
