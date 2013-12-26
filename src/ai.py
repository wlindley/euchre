import logging
import random

import euchre
import retriever
import game

logging.getLogger().setLevel(logging.DEBUG)

class TurnTaker(object):
	instance = None
	@classmethod
	def getInstance(cls):
		if None != cls.instance:
			return cls.instance
		return TurnTaker(RobotFactory.getInstance(), retriever.GameStatusRetriever.getInstance(euchre.WINNING_SCORE), retriever.TurnRetriever.getInstance())

	def __init__(self, robotRetriever, gameStatusRetriever, turnRetriever):
		self._robotFactory = robotRetriever
		self._gameStatusRetriever = gameStatusRetriever
		self._turnRetriever = turnRetriever

	def takeTurns(self, gameObj):
		playerId = self._turnRetriever.retrieveTurn(gameObj)
		robot = self._robotFactory.buildRobot(playerId)
		while None != robot:
			status = self._gameStatusRetriever.retrieveGameStatus(gameObj)
			if "trump_selection" == status:
				robot.selectTrump(playerId, gameObj)
			elif "trump_selection_2" == status:
				robot.selectTrump2(playerId, gameObj)
			elif "discard" == status:
				robot.discardCard(playerId, gameObj)
			elif "round_in_progress" == status:
				robot.playCard(playerId, gameObj)
			playerId = self._turnRetriever.retrieveTurn(gameObj)
			robot = self._robotFactory.buildRobot(playerId)

class RobotFactory(object):
	instance = None
	@classmethod
	def getInstance(cls):
		if None != cls.instance:
			return cls.instance
		return RobotFactory()

	def __init__(self):
		pass

	def buildRobot(self, playerId):
		if None != playerId and playerId.startswith("euchre_robot_random"):
			return RandomCardPlayerAI.getInstance()
		return None

class BasePlayerAI(object):
	def __init__(self, handRetriever):
		self._handRetriever = handRetriever

	def _getPlayerForId(self, playerId):
		return game.Player.getInstance(playerId)

	def selectTrump(self, playerId, gameObj):
		pass

	def selectTrump2(self, playerId, gameObj):
		pass

	def discardCard(self, playerId, gameObj):
		pass

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

	def selectTrump(self, playerId, gameObj):
		gameObj.selectTrump(self._getPlayerForId(playerId), euchre.SUIT_NONE)

	def selectTrump2(self, playerId, gameObj):
		gameObj.selectTrump(self._getPlayerForId(playerId), random.choice([euchre.SUIT_CLUBS, euchre.SUIT_DIAMONDS, euchre.SUIT_SPADES, euchre.SUIT_HEARTS]))

	def discardCard(self, playerId, gameObj):
		hand = self._handRetriever.retrieveHand(playerId, gameObj)
		gameObj.discardCard(self._getPlayerForId(playerId), random.choice(hand))

	def playCard(self, playerId, gameObj):
		hand = self._handRetriever.retrieveHand(playerId, gameObj)
		try:
			gameObj.playCard(self._getPlayerForId(playerId), random.choice(hand))
		except game.GameRuleException as e:
			logging.error("Caught exception while random AI was playing card: %s" % e)