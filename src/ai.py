import logging
import random

import euchre
import retriever

logging.getLogger().setLevel(logging.DEBUG)

class TurnTaker(object):
	instance = None
	@classmethod
	def getInstance(cls):
		if None != cls.instance:
			return cls.instance
		return TurnTaker(retriever.RobotRetriever.getInstance(), retriever.GameStatusRetriever.getInstance(euchre.WINNING_SCORE), retriever.TurnRetriever.getInstance())

	def __init__(self, robotRetriever, gameStatusRetriever, turnRetriever):
		self._robotRetriever = robotRetriever
		self._gameStatusRetriever = gameStatusRetriever
		self._turnRetriever = turnRetriever

	def takeTurns(self, gameObj):
		playerId = self._turnRetriever.retrieveTurn(gameObj, None)
		robot = self._robotRetriever.retrieveRobotById(playerId)
		while None != robot:
			status = self._gameStatusRetriever.retrieveGameStatus(gameObj)
			if "trump_selection" == status:
				robot.selectTrump(playerId, gameObj)
			elif "discard" == status:
				robot.discard(playerId, gameObj)
			elif "round_in_progress" == status:
				robot.playCard(playerId, gameObj)
			playerId = self._turnRetriever.retrieveTurn(gameObj, None)
			robot = self._robotRetriever.retrieveRobotById(playerId)

class BasePlayerAI(object):
	def __init__(self, handRetriever, upCardRetriever):
		self._handRetriever = handRetriever
		self._upCardRetriever = upCardRetriever

	def selectTrump(self, playerId, gameObj):
		pass

	def discard(self, playerId, gameObj):
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

	def discard(self, playerId, gameObj):
		raise Exception("Not Yet Implemented")

	def playCard(self, playerId, gameObj):
		hand = self._handRetriever.retrieveHand(playerId, gameObj)
		gameObj.playCard(playerId, random.choice(hand))