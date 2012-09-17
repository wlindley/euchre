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
		prevDeck = self.deck.remainingCards[:]
		self.deck.shuffle()
		self.assertNotEqual(prevDeck, self.deck.remainingCards)

	def testShuffleDoesNotAlwaysGiveSameResult(self):
		self.deck.shuffle()
		prevDeck = self.deck.remainingCards[:]
		self.deck.shuffle()
		self.assertNotEqual(prevDeck, self.deck.remainingCards)

	def testCanBuildDeckWithCardValueRange(self):
		minValue = 6
		maxValue = euchre.VALUE_JACK
		self.deck = euchre.Deck(minValue=minValue, maxValue=maxValue)
		cardsPerSuit = maxValue - minValue + 1
		self.assertEqual(cardsPerSuit * euchre.NUM_SUITS, len(self.deck.remainingCards))
		for card in self.deck.remainingCards:
			self.assertTrue(card.value >= minValue and card.value <= maxValue)

	def testDealingCardRemovesItFromDeck(self):
		initialNumCards = len(self.deck.remainingCards)
		dealtCards = self.deck.deal(1)
		self.assertEqual(1, len(dealtCards))
		self.assertEqual(initialNumCards - 1, len(self.deck.remainingCards))
		self.assertEqual(0, self.deck.remainingCards.count(dealtCards[0]))

	def testDealingManyCardRemovesThemFromDeck(self):
		cardsToDeal = 5
		initialNumCards = len(self.deck.remainingCards)
		dealtCards = self.deck.deal(cardsToDeal)
		self.assertEqual(cardsToDeal, len(dealtCards))
		self.assertEqual(initialNumCards - cardsToDeal, len(self.deck.remainingCards))
		for dealtCard in dealtCards:
			self.assertEqual(0, self.deck.remainingCards.count(dealtCard))

class HandTest(unittest.TestCase):
	hand = None

	def setUp(self):
		self.hand = euchre.Hand()

	def testHandContainsCardsAddedToIt(self):
		cards = [euchre.Card(euchre.SUIT_SPADES, 8), euchre.Card(euchre.SUIT_HEARTS, 3), euchre.Card(euchre.SUIT_CLUBS, euchre.VALUE_KING)]
		self.hand.add(cards)
		for card in cards:
			self.assertEqual(1, self.hand._cards.count(card))

	def testPlayingCardRemovesItFromHand(self):
		cards = [euchre.Card(euchre.SUIT_SPADES, 8), euchre.Card(euchre.SUIT_HEARTS, 3), euchre.Card(euchre.SUIT_CLUBS, euchre.VALUE_KING)]
		self.hand.add(cards)
		self.hand.play(cards[1])
		self.assertEqual(1, self.hand._cards.count(cards[0]))
		self.assertEqual(0, self.hand._cards.count(cards[1]))
		self.assertEqual(1, self.hand._cards.count(cards[2]))

	def testGetCardsReturnsListOfCardsInHand(self):
		cards = [euchre.Card(euchre.SUIT_SPADES, 8), euchre.Card(euchre.SUIT_HEARTS, 3), euchre.Card(euchre.SUIT_CLUBS, euchre.VALUE_KING)]
		self.hand.add(cards)
		cardList = self.hand.getCards()
		self.assertEqual(cards, cardList)

if __name__ == "__main__":
	unittest.main()
