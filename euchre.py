import random

SUIT_NONE = 0
SUIT_CLUBS = 1
SUIT_DIAMONDS = 2
SUIT_SPADES = 3
SUIT_HEARTS = 4
NUM_SUITS = 4

VALUE_NONE = 0
VALUE_MIN = 2
VALUE_JACK = 11
VALUE_QUEEN = 12
VALUE_KING = 13
VALUE_ACE = 14
VALUE_LEFT_BOWER = 15
VALUE_RIGHT_BOWER = 16

NUM_CARDS_IN_DECK = 52
NUM_CARDS_IN_SUIT = 13

class Card(object):
	suit = 0
	value = 0

	def __init__(self, suit = 0, value = 0):
		self.suit = suit
		self.value = value

	def __eq__(self, other):
		if not other:
			return False
		if not isinstance(other, Card):
			return other.__eq__(self)
		return self.value == other.value and self.suit == other.suit

	def __str__(self):
		return "Card suit %s, value %s" % (self.suit, self.value)

	def __repr__(self):
		return "Card(%s, %s)" % (self.suit, self.value)

class Deck(object):
	remainingCards = []

	def __init__(self, minValue=VALUE_MIN, maxValue=VALUE_ACE):
		self.remainingCards = []
		for curSuit in range(SUIT_CLUBS, SUIT_HEARTS + 1):
			for curValue in range(minValue, maxValue + 1):
				self.remainingCards.append(Card(curSuit, curValue))

	def shuffle(self):
		random.shuffle(self.remainingCards)

	def deal(self, numCards):
		cards = self.remainingCards[:numCards]
		self.remainingCards = self.remainingCards[numCards:]
		return cards

class Hand(object):
	_cards = None

	def __init__(self):
		self._cards = []

	def add(self, cards):
		self._cards.extend(cards)

	def play(self, card):
		if self._cards.count(card) > 0:
			self._cards.remove(card)

	def getCards(self):
		return self._cards[:]

class Trick(object):
	playedCards = []
	ledSuit = None

	def add(self, card):
		if None == self.ledSuit:
			self.ledSuit = card.suit
		self.playedCards.append(card)

class TrickEvaluator(object):
	trumpSuit = SUIT_NONE

	def setTrump(self, trumpSuit):
		self.trumpSuit = trumpSuit

	def evaluateTrick(self, trick):
		highestTrumpValue = -1
		highestLedValue = -1
		highestTrumpCard = None
		highestLedCard = None
		for card in trick.playedCards:
			if card.suit == self.trumpSuit and card.value > highestTrumpValue:
				highestTrumpValue = card.value
				highestTrumpCard = card
			if card.suit == trick.ledSuit and card.value > highestLedValue:
				highestLedValue = card.value
				highestLedCard = card

		if highestTrumpCard:
			return highestTrumpCard
		if highestLedCard:
			return highestLedCard
		return None
