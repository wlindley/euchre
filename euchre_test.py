#!/usr/bin/env python
import unittest
import euchre

class DeckTest(unittest.TestCase):
	deck = None

	def setUp(self):
		self.deck = euchre.Deck()

	def tearDown(self):
		self.deck = None

	def testDeckHas52CardsByDefault(self):
		self.assertEqual(euchre.NUM_CARDS_IN_DECK, len(self.deck.remainingCards))

	def testDeckHas13CardsOfEachSuit(self):
		suitCounts = [0 for i in range(euchre.SUIT_HEARTS + 1)]
		for card in self.deck.remainingCards:
			suitCounts[card.suit] += 1
		self.assertEqual(0, suitCounts[0])
		for i in range(1, euchre.NUM_SUITS + 1):
			self.assertEqual(euchre.NUM_CARDS_IN_SUIT, suitCounts[i])

	def testShuffleChangesOrderOfCards(self):
		prevDeck = [card for card in self.deck.remainingCards]
		self.deck.shuffle()
		self.assertNotEqual(prevDeck, self.deck.remainingCards)

	def testShuffleDoesNotAlwaysGiveSameResult(self):
		self.deck.shuffle()
		prevDeck = [card for card in self.deck.remainingCards]
		self.deck.shuffle()
		self.assertNotEqual(prevDeck, self.deck.remainingCards)

if __name__ == "__main__":
	unittest.main()
