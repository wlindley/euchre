#!/usr/bin/env python
import testhelper
import json
import random
from mockito import *

from src import ai
from src import euchre
from src import retriever
from src import model
from src import game

class TurnTakerTest(testhelper.TestCase):
	def setUp(self):
		self.robotFactory = testhelper.createSingletonMock(ai.RobotFactory)
		self.gameStatusRetriever = testhelper.createSingletonMock(retriever.GameStatusRetriever)
		self.turnRetriever = testhelper.createSingletonMock(retriever.TurnRetriever)

		self.players = ["1239804adjf", "32409afslk", "euchre_robot_random_0", "euchre_robot_random_1"]
		self.randomAI = testhelper.createSingletonMock(ai.RandomCardPlayerAI)
		self.gameObj = testhelper.createMock(model.GameModel)
		self.status = ""

		self.doTraining()
		self.buildTestObj()

	def buildTestObj(self):
		self.testObj = ai.TurnTaker.getInstance()

	def doTraining(self):
		when(self.robotFactory).buildRobot("euchre_robot_random_0").thenReturn(self.randomAI)
		when(self.robotFactory).buildRobot("euchre_robot_random_1").thenReturn(self.randomAI)
		when(self.gameStatusRetriever).retrieveGameStatus(self.gameObj).thenReturn(self.status)
		when(self.turnRetriever).retrieveTurn(self.gameObj).thenReturn(self.players[2]).thenReturn(self.players[3]).thenReturn(self.players[0])

	def trigger(self):
		self.testObj.takeTurns(self.gameObj)

	def testTakeTurnsAllowsAIPlayersToSelectTrump(self):
		self.status = "trump_selection"
		self.doTraining()
		self.trigger()
		inorder.verify(self.randomAI).selectTrump("euchre_robot_random_0", self.gameObj)
		inorder.verify(self.randomAI).selectTrump("euchre_robot_random_1", self.gameObj)

	def testTakeTurnsAllowsAIPlayersToSelectTrumpInSecondBiddingPhase(self):
		self.status = "trump_selection_2"
		self.doTraining()
		self.trigger()
		verify(self.randomAI).selectTrump2("euchre_robot_random_0", self.gameObj)

	def testTakeTurnsAllowsAIPlayersToPlayCards(self):
		self.status = "discard"
		self.doTraining()
		self.trigger()
		inorder.verify(self.randomAI).playCard("euchre_robot_random_0", self.gameObj)
		inorder.verify(self.randomAI).playCard("euchre_robot_random_1", self.gameObj)

	def testTakeTurnsAllowsAIPlayersToPlayCards(self):
		when(self.gameStatusRetriever).retrieveGameStatus(self.gameObj).thenReturn("discard").thenReturn("round_in_progress")
		self.trigger()
		inorder.verify(self.randomAI).discardCard("euchre_robot_random_0", self.gameObj)
		inorder.verify(self.randomAI).playCard("euchre_robot_random_1", self.gameObj)

class RobotFactoryTest(testhelper.TestCase):
	def setUp(self):
		self.buildTestObj()

	def buildTestObj(self):
		self.testObj = ai.RobotFactory.getInstance()

	def runTest(self, playerId, expectedType):
		result = self.testObj.buildRobot(playerId)
		self.assertIsInstance(result, expectedType)

	def testForUnknownPlayerId(self):
		self.runTest("2309482033", type(None))

	def testForRandomCardPlayerAI(self):
		self.runTest("euchre_robot_random_0", ai.RandomCardPlayerAI)

	def testForRandomCardPlayerAIWithDifferentName(self):
		self.runTest("euchre_robot_random_1", ai.RandomCardPlayerAI)

class BasePlayerAITest(testhelper.TestCase):
	def setUp(self):
		self.handRetriever = testhelper.createSingletonMock(retriever.HandRetriever)
		self.upCardRetriever = testhelper.createSingletonMock(retriever.UpCardRetriever)
		self.playerId = "2304asdfoi34"
		self.playerObj = game.Player.getInstance(self.playerId)
		self.gameObj = testhelper.createMock(euchre.Game)
		self.hand = [
			euchre.Card.getInstance(euchre.SUIT_CLUBS, 3),
			euchre.Card.getInstance(euchre.SUIT_HEARTS, 8),
			euchre.Card.getInstance(euchre.SUIT_SPADES, 10),
			euchre.Card.getInstance(euchre.SUIT_DIAMONDS, 12),
			euchre.Card.getInstance(euchre.SUIT_CLUBS, 14)
		]

		when(self.handRetriever).retrieveHand(self.playerId, self.gameObj).thenReturn(self.hand)

	def triggerSelectTrump(self):
		self.testObj.selectTrump(self.playerId, self.gameObj)

	def triggerSelectTrump2(self):
		self.testObj.selectTrump2(self.playerId, self.gameObj)

	def triggerDiscardCard(self):
		self.testObj.discardCard(self.playerId, self.gameObj)

	def triggerPlayCard(self):
		self.testObj.playCard(self.playerId, self.gameObj)

class RandomCardPlayerAITest(BasePlayerAITest):
	def buildTestObj(self):
		self.testObj = ai.RandomCardPlayerAI.getInstance()

	def setUp(self):
		super(RandomCardPlayerAITest, self).setUp()
		self.buildTestObj()

	def testPlaysAnyCardFromHand(self):
		self.selectedCard = None
		def tmp(playerObj, card):
			self.playedPlayer = playerObj
			self.selectedCard = card
		self.gameObj.playCard = tmp

		self.triggerPlayCard()

		self.assertEqual(self.playerObj, self.playedPlayer)
		self.assertIsNotNone(self.selectedCard)
		self.assertIn(self.selectedCard, self.hand)

	def testSelectTrumpNeverSelectsUpCardSuit(self):
		self.selectedTrump = None
		def tmp(playerObj, suit):
			self.playedPlayer = playerObj
			self.selectedTrump = suit
		self.gameObj.selectTrump = tmp

		self.triggerSelectTrump()

		self.assertEqual(self.playerObj, self.playedPlayer)
		self.assertEqual(euchre.SUIT_NONE, self.selectedTrump)

	def testSelectTrumpSelectsARandomSuitWhenNoUpCard(self):
		self.selectedTrump = None
		def tmp(playerObj, suit):
			self.playedPlayer = playerObj
			self.selectedTrump = suit
		self.gameObj.selectTrump = tmp

		self.triggerSelectTrump2()

		self.assertEqual(self.playerObj, self.playedPlayer)
		self.assertIsNotNone(self.selectedTrump)
		self.assertTrue(self.selectedTrump in [euchre.SUIT_CLUBS, euchre.SUIT_DIAMONDS, euchre.SUIT_SPADES, euchre.SUIT_HEARTS])

	def testDiscardDiscardsARandomCardFromHand(self):
		self.selectedCard = None
		def tmp(playerObj, card):
			self.playedPlayer = playerObj
			self.selectedCard = card
		self.gameObj.discardCard = tmp

		self.triggerDiscardCard()

		self.assertEqual(self.playerObj, self.playedPlayer)
		self.assertIsNotNone(self.selectedCard)
		self.assertIn(self.selectedCard, self.hand)