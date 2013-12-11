#!/usr/bin/env python
import testhelper
import json
import random
from mockito import *

from src import ai
from src import euchre
from src import retriever

class BasePlayerAITest(testhelper.TestCase):
	def setUp(self):
		self.handRetriever = testhelper.createSingletonMock(retriever.HandRetriever)
		self.playerId = "2304asdfoi34"
		self.gameObj = testhelper.createMock(euchre.Game)
		self.hand = [
			euchre.Card.getInstance(euchre.SUIT_CLUBS, 3),
			euchre.Card.getInstance(euchre.SUIT_HEARTS, 8),
			euchre.Card.getInstance(euchre.SUIT_SPADES, 10),
			euchre.Card.getInstance(euchre.SUIT_DIAMONDS, 12),
			euchre.Card.getInstance(euchre.SUIT_CLUBS, 14)
		]

		when(self.handRetriever).retrieveHand(self.playerId).thenReturn(self.hand)

	def trigger(self):
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
		self.trigger()
		self.assertNotEqual(None, self.selectedCard)
		self.assertTrue(self.selectedCard in self.hand)