import logging
import random

import euchre
import retriever

logging.getLogger().setLevel(logging.DEBUG)

class BasePlayerAI(object):
	def __init__(self, handRetriever):
		self._handRetriever = handRetriever

	def playCard(self, playerId, gameObj):
		pass

class RandomCardPlayerAI(BasePlayerAI):
	instance = None
	@classmethod
	def getInstance(cls):
		if None != cls.instance:
			return cls.instance
		return RandomCardPlayerAI(retriever.HandRetriever.getInstance())

	def __init__(self, handRetriever):
		super(RandomCardPlayerAI, self).__init__(handRetriever)

	def playCard(self, playerId, gameObj):
		hand = self._handRetriever.retrieveHand(playerId)
		gameObj.playCard(playerId, hand[random.randrange(0, len(hand))])