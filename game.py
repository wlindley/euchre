class Player(object):
	def __init__(self, playerId):
		self.playerId = playerId

class InvalidPlayerException(Exception):
	pass

class GameRuleException(Exception):
	pass

class TurnTracker(object):
	def __init__(self, players):
		self.players = players
		self._currentIndex = 0

	def getCurrentPlayerId(self):
		return self.players[self._currentIndex].playerId

	def advanceTurn(self):
		self._currentIndex = (self._currentIndex + 1) % len(self.players)
