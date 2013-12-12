#!/usr/bin/env python
import testhelper
import json
import random
from mockito import *

from src import ai
from src import euchre
from src import retriever
from src import model

class TurnTakerTest(testhelper.TestCase):
	def setUp(self):
		self.robotRetriever = testhelper.createSingletonMock(retriever.RobotRetriever)
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
		when(self.robotRetriever).retrieveRobotById("euchre_robot_random_0").thenReturn(self.randomAI)
		when(self.robotRetriever).retrieveRobotById("euchre_robot_random_1").thenReturn(self.randomAI)
		when(self.gameStatusRetriever).retrieveGameStatus(self.gameObj).thenReturn(self.status)
		when(self.turnRetriever).retrieveTurn(self.gameObj, None).thenReturn(self.players[2]).thenReturn(self.players[3]).thenReturn(self.players[0])

	def trigger(self):
		self.testObj.takeTurns(self.gameObj)

	def testTakeTurnsAllowsAIPlayersToSelectTrump(self):
		self.status = "trump_selection"
		self.doTraining()
		self.trigger()
		inorder.verify(self.randomAI).selectTrump("euchre_robot_random_0", self.gameObj)
		inorder.verify(self.randomAI).selectTrump("euchre_robot_random_1", self.gameObj)

	def testTakeTurnsAllowsAIPlayersToPlayCards(self):
		self.status = "round_in_progress"
		self.doTraining()
		self.trigger()
		inorder.verify(self.randomAI).playCard("euchre_robot_random_0", self.gameObj)
		inorder.verify(self.randomAI).playCard("euchre_robot_random_1", self.gameObj)

class BasePlayerAITest(testhelper.TestCase):
	def setUp(self):
		self.handRetriever = testhelper.createSingletonMock(retriever.HandRetriever)
		self.upCardRetriever = testhelper.createSingletonMock(retriever.UpCardRetriever)
		self.playerId = "2304asdfoi34"
		self.gameObj = testhelper.createMock(euchre.Game)
		self.hand = [
			euchre.Card.getInstance(euchre.SUIT_CLUBS, 3),
			euchre.Card.getInstance(euchre.SUIT_HEARTS, 8),
			euchre.Card.getInstance(euchre.SUIT_SPADES, 10),
			euchre.Card.getInstance(euchre.SUIT_DIAMONDS, 12),
			euchre.Card.getInstance(euchre.SUIT_CLUBS, 14)
		]
		self.upCard = euchre.Card.getInstance(euchre.SUIT_HEARTS, 5)

		when(self.handRetriever).retrieveHand(self.playerId, self.gameObj).thenReturn(self.hand)
		when(self.upCardRetriever).retrieveUpCard(self.gameObj).thenReturn(self.upCard)

	def triggerSelectTrump(self):
		self.testObj.selectTrump(self.playerId, self.gameObj)

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
		def tmp(pid, card):
			self.selectedCard = card
		self.gameObj.playCard = tmp
		self.triggerPlayCard()
		self.assertNotEqual(None, self.selectedCard)
		self.assertTrue(self.selectedCard in self.hand)

	def testSelectTrumpNeverSelectsUpCardSuit(self):
		self.selectedTrump = None
		def tmp(pid, suit):
			self.selectedTrump = suit
		self.gameObj.selectTrump = tmp
		self.triggerSelectTrump()
		self.assertEqual(euchre.SUIT_NONE, self.selectedTrump)

	def testSelectTrumpSelectsARandomSuitWhenNoUpCard(self):
		when(self.upCardRetriever).retrieveUpCard(self.gameObj).thenReturn(None)
		self.selectedTrump = None
		def tmp(pid, suit):
			self.selectedTrump = suit
		self.gameObj.selectTrump = tmp
		self.triggerSelectTrump()
		self.assertNotEqual(None, self.selectedTrump)
		self.assertTrue(self.selectedTrump in [euchre.SUIT_CLUBS, euchre.SUIT_DIAMONDS, euchre.SUIT_SPADES, euchre.SUIT_HEARTS])