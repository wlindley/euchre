import logging
import random

import euchre
import retriever

logging.getLogger().setLevel(logging.DEBUG)

class BasePlayerAI(object):
	def __init__(self, handRetriever, upCardRetriever):
		self._handRetriever = handRetriever
		self._upCardRetriever = upCardRetriever

	def selectTrump(self, playerId, gameObj):
		pass

	def playCard(self, playerId, gameObj):
		pass

class RandomCardPlayerAI(BasePlayerAI):
	instance = None
	@classmethod
	def getInstance(cls):
		if None != cls.instance:
			return cls.instance
		return RandomCardPlayerAI(retriever.HandRetriever.getInstance(), retriever.UpCardRetriever.getInstance())

	def __init__(self, handRetriever, upCardRetriever):
		super(RandomCardPlayerAI, self).__init__(handRetriever, upCardRetriever)

	def selectTrump(self, playerId, gameObj):
		upCard = self._upCardRetriever.retrieveUpCard(gameObj)
		if None != upCard:
			gameObj.selectTrump(playerId, euchre.SUIT_NONE)
		else:
			gameObj.selectTrump(playerId, random.choice([euchre.SUIT_CLUBS, euchre.SUIT_DIAMONDS, euchre.SUIT_SPADES, euchre.SUIT_HEARTS]))

	def playCard(self, playerId, gameObj):
		hand = self._handRetriever.retrieveHand(playerId, gameObj)
		gameObj.playCard(playerId, random.choice(hand))