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