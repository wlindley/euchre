import euchre

class DealerRetriever(object):
	instance = None
	@classmethod
	def getInstance(cls):
		if None != cls.instance:
			return cls.instance
		return DealerRetriever()

	def retrieveDealer(self, gameObj):
		return gameObj.getPlayers()[0].playerId
