class Player(object):
	def __init__(self, playerId):
		self.playerId = playerId

class InvalidPlayerException(Exception):
	pass

class GameRuleException(Exception):
	pass
