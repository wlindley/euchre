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

class HandRetriever(object):
	instance = None
	@classmethod
	def getInstance(cls):
		if None != cls.instance:
			return cls.instance
		return HandRetriever()

	def __init__(self):
		super(HandRetriever, self).__init__()

	def getHand(self, playerId, gameObj):
		sequenceObj = gameObj.getSequence()
		if None == sequenceObj:
			return []
		roundObj = sequenceObj.getRound()
		if playerId not in roundObj.hands:
			return []
		return roundObj.hands[playerId]

class TurnRetriever(object):
	instance = None
	@classmethod
	def getInstance(cls):
		if None != cls.instance:
			return cls.instance
		return TurnRetriever()

	def retrieveTurn(self, gameObj):
		sequence = gameObj.getSequence()
		if None == sequence:
			return None
		if euchre.Sequence.STATE_TRUMP_SELECTION == sequence.getState() or euchre.Sequence.STATE_TRUMP_SELECTION_2 == sequence.getState():
			turnTracker = sequence.getTrumpSelector().getTurnTracker()
		elif euchre.Sequence.STATE_PLAYING_ROUND == sequence.getState():
			turnTracker = sequence.getRound().getTurnTracker()
		else:
			return None
		return turnTracker.getCurrentPlayerId()

class UpCardRetriever(object):
	instance = None
	@classmethod
	def getInstance(cls):
		if None != cls.instance:
			return cls.instance
		return UpCardRetriever()

	def retrieveUpCard(self, gameObj):
		sequence = gameObj.getSequence()
		if euchre.Sequence.STATE_TRUMP_SELECTION == sequence.getState():
			return sequence.getUpCard()
		return None
