import random
import game
import logging

logging.getLogger().setLevel(logging.DEBUG)

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

NUM_PLAYERS = 4
HAND_SIZE = 5
MIN_4_PLAYER_CARD_VALUE = 9

WINNING_SCORE = 10

class Card(object):
	instance = None
	@classmethod
	def getInstance(cls, suit=SUIT_NONE, value=0):
		if None != cls.instance:
			return cls.instance
		return Card(suit, value)

	def __init__(self, suit=SUIT_NONE, value=0):
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
	instance = None
	@classmethod
	def getInstance(cls, minValue=VALUE_MIN, maxValue=VALUE_ACE):
		if None != cls.instance:
			return cls.instance
		return Deck(minValue, maxValue)

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

	def peekTop(self):
		return self.remainingCards[0]

class Trick(object):
	instance = None
	@classmethod
	def getInstance(cls, trumpSuit):
		if None != cls.instance:
			return cls.instance
		return Trick(CardTranslator.getInstance(trumpSuit))

	def __init__(self, cardTranslator):
		self._playedCards = {}
		self._ledSuit = SUIT_NONE
		self._cardTranslator = cardTranslator

	def add(self, player, card):
		if SUIT_NONE == self._ledSuit:
			translatedCard = self._cardTranslator.translateCard(card)
			self._ledSuit = translatedCard.suit
		if player.playerId in self._playedCards:
			raise game.GameRuleException("Player with id %s has already played a card in this trick" % player.playerId)
		self._playedCards[player.playerId] = card

	def isComplete(self):
		return len(self._playedCards) >= NUM_PLAYERS

	def getLedSuit(self):
		return self._ledSuit

	def getPlayedCards(self):
		return self._playedCards

class CardTranslator(object):
	instance = None
	@classmethod
	def getInstance(cls, trumpSuit):
		if None != cls.instance:
			return cls.instance
		return CardTranslator(trumpSuit)

	def __init__(self, trumpSuit):
		super(CardTranslator, self).__init__()
		self._trumpSuit = trumpSuit

	def translateCard(self, card):
		translatedCard = Card.getInstance(card.suit, card.value)
		if SUIT_NONE == self._trumpSuit:
			return translatedCard
		if self._trumpSuit == card.suit and VALUE_JACK == card.value:
			translatedCard.value = VALUE_RIGHT_BOWER
		elif ((self._trumpSuit + 1) % 4) + 1 == card.suit and VALUE_JACK == card.value:
			translatedCard.suit = self._trumpSuit
			translatedCard.value = VALUE_LEFT_BOWER
		return translatedCard

	def setTrump(self, trump):
		self._trumpSuit = trump

class TrickEvaluator(object):
	instance = None
	@classmethod
	def getInstance(cls, trump=SUIT_NONE):
		if None != cls.instance:
			return cls.instance
		return TrickEvaluator(CardTranslator.getInstance(trump), trump)

	def __init__(self, cardTranslator, trump=SUIT_NONE):
		self._trumpSuit = trump
		self._cardTranslator = cardTranslator

	def setTrump(self, trumpSuit):
		self._trumpSuit = trumpSuit
		self._cardTranslator.setTrump(trumpSuit)

	def getTrump(self):
		return self._trumpSuit

	def evaluateTrick(self, trick):
		highestTrumpValue = -1
		highestLedValue = -1
		highestTrumpCard = None
		highestLedCard = None
		highestTrumpId = None
		highestLedId = None
		for playerId, card in trick.getPlayedCards().iteritems():
			translatedCard = self._cardTranslator.translateCard(card)
			cardSuit = translatedCard.suit
			cardValue = translatedCard.value
			if cardSuit == self._trumpSuit and cardValue > highestTrumpValue:
				highestTrumpValue = cardValue
				highestTrumpCard = card
				highestTrumpId = playerId
			if cardSuit == trick.getLedSuit() and cardValue > highestLedValue:
				highestLedValue = cardValue
				highestLedCard = card
				highestLedId = playerId

		if highestTrumpCard:
			return highestTrumpId
		if highestLedCard:
			return highestLedId
		return None

class Round(object):
	instance = None
	@classmethod
	def getInstance(cls, players, hands, trumpSuit=SUIT_NONE):
		if None != cls.instance:
			return cls.instance
		return Round(game.TurnTracker.getInstance(players), TrickEvaluator.getInstance(trumpSuit), hands, CardTranslator.getInstance(trumpSuit))

	MAX_HAND_SIZE = 5

	def __init__(self, turnTracker, trickEvaluator, hands, cardTranslator):
		self._hands = hands
		self._curTrick = Trick.getInstance(trickEvaluator.getTrump())
		self._prevTricks = []
		self._scores = {}
		self._trickEvaluator = trickEvaluator
		self._turnTracker = turnTracker
		self._cardTranslator = cardTranslator

	def playCard(self, player, card):
		if None == player or player.playerId not in self._hands:
			raise game.InvalidPlayerException("Player with id %s is not a member of this round" % (None if None == player else player.playerId))
		if card not in self._hands[player.playerId]:
			raise game.GameRuleException("Player with id %s does not have card %s in their hand" % (player.playerId, card))
		if self._turnTracker.getCurrentPlayerId() != player.playerId:
			raise game.GameRuleException("It is not player %s's turn, current player id is %s" % (player.playerId, self._turnTracker.getCurrentPlayerId()))
		ledSuit = self._curTrick.getLedSuit()
		translatedCard = self._cardTranslator.translateCard(card)
		if SUIT_NONE != ledSuit and ledSuit != translatedCard.suit:
			for heldCard in self._hands[player.playerId]:
				translatedHeldCard = self._cardTranslator.translateCard(heldCard)
				if ledSuit == translatedHeldCard.suit:
					raise game.GameRuleException("Player with id %s must follow suit, cannot play %s when led suit is %s and %s is in their hand" % (player.playerId, card, ledSuit, heldCard))

		self._hands[player.playerId].remove(card)
		self._curTrick.add(player, card)
		self._nextTurn()

		if self._curTrick.isComplete():
			self._nextTrick()

	def addCardToHand(self, player, card):
		if None == player or player.playerId not in self._hands:
			raise game.InvalidPlayerException("Player with id %s is not a member of this round" % (None if None == player else player.playerId))
		self._hands[player.playerId].append(card)

	def discardCard(self, player, card):
		if None == player or player.playerId not in self._hands:
			raise game.InvalidPlayerException("Player with id %s is not a member of this round" % (None if None == player else player.playerId))
		if Round.MAX_HAND_SIZE >= len(self._hands[player.playerId]):
			raise game.GameRuleException("Player with id %s does not have too many cards in hand and thus cannot discard any" % player.playerId)
		try:
			self._hands[player.playerId].remove(card)
		except ValueError:
			raise game.GameRuleException("Player with id %s does not have card %s in their hand" % (player.playerId, card))

	def getHands(self):
		return self._hands

	def isComplete(self):
		return HAND_SIZE <= len(self._prevTricks)

	def getScore(self, playerId):
		if playerId in self._scores:
			return self._scores[playerId]
		return 0

	def setTrump(self, trumpSuit):
		self._trickEvaluator.setTrump(trumpSuit)

	def getTrump(self):
		return self._trickEvaluator.getTrump()

	def getTurnTracker(self):
		return self._turnTracker

	def getCurrentTrick(self):
		return self._curTrick

	def getPreviousTricks(self):
		return self._prevTricks

	def _nextTrick(self):
		winner = self._trickEvaluator.evaluateTrick(self._curTrick)
		self._incrementScore(winner)
		self._prevTricks.append(self._curTrick)
		self._curTrick = Trick.getInstance(self._trickEvaluator.getTrump())
		self._setPlayerTurn(winner)

	def _incrementScore(self, playerId):
		if playerId in self._scores:
			self._scores[playerId] += 1
		else:
			self._scores[playerId] = 1

	def _nextTurn(self):
		self._turnTracker.advanceTurn()

	def _setPlayerTurn(self, playerId):
		self._turnTracker.setTurnByPlayerId(playerId)

class TrumpSelector(object):
	instance = None
	@classmethod
	def getInstance(cls, players, availableTrump=SUIT_NONE):
		if None != cls.instance:
			return cls.instance
		return TrumpSelector(game.TurnTracker.getInstance(players), availableTrump)

	def __init__(self, turnTracker, availableTrump=SUIT_NONE):
		self._turnTracker = turnTracker
		self._availableTrump = availableTrump
		self._selectedTrump = SUIT_NONE
		self._selectingPlayerId = None

	def getAvailableTrump(self):
		return self._availableTrump

	def getSelectedTrump(self):
		return self._selectedTrump

	def getSelectingPlayerId(self):
		return self._selectingPlayerId

	def getTurnTracker(self):
		return self._turnTracker

	def selectTrump(self, player, trumpSuit):
		if self._turnTracker.getCurrentPlayerId() != player.playerId:
			raise game.GameRuleException("Player %s cannot select the trump right now, it is player %s's turn" % (player.playerId, self._turnTracker.getCurrentPlayerId()))
		if SUIT_NONE != trumpSuit:
			if SUIT_NONE != self._availableTrump and self._availableTrump != trumpSuit:
				raise game.GameRuleException("Cannot choose suit %s as trump while only suit %s is available" % (trumpSuit, self._availableTrump))
			self._recordTrumpSelection(player, trumpSuit)
		self._turnTracker.advanceTurn()

	def isComplete(self):
		return (SUIT_NONE != self._selectedTrump) or (1 <= self._turnTracker.getAllTurnCount())

	def reset(self):
		self._turnTracker.reset()
		self._availableTrump = SUIT_NONE
		self._selectedTrump = SUIT_NONE

	def _recordTrumpSelection(self, player, trumpSuit):
		self._selectedTrump = trumpSuit
		self._selectingPlayerId = player.playerId

class Sequence(object):
	STATE_TRUMP_SELECTION = "STATE_TRUMP_SELECTION"
	STATE_TRUMP_SELECTION_2 = "STATE_TRUMP_SELECTION_2"
	STATE_TRUMP_SELECTION_FAILED = "STATE_TRUMP_SELECTION_FAILED"
	STATE_DISCARD = "STATE_DISCARD"
	STATE_PLAYING_ROUND = "STATE_PLAYING_ROUND"
	STATE_COMPLETE = "STATE_COMPLETE"
	STATE_INVALID = "STATE_INVALID"

	instance = None
	@classmethod
	def getInstance(cls, players, hands, upCard=None):
		if None != cls.instance:
			return cls.instance
		suit = SUIT_NONE
		if None != upCard:
			suit = upCard.suit
		return Sequence(TrumpSelector.getInstance(players, suit), Round.getInstance(players, hands), upCard)

	def __init__(self, trumpSelector, round, upCard):
		self._trumpSelector = trumpSelector
		self._round = round
		self._upCard = upCard

	def getState(self):
		if SUIT_NONE == self._trumpSelector.getSelectedTrump():
			if SUIT_NONE == self._trumpSelector.getAvailableTrump():
				if self._trumpSelector.isComplete():
					return Sequence.STATE_TRUMP_SELECTION_FAILED
				return Sequence.STATE_TRUMP_SELECTION_2
			return Sequence.STATE_TRUMP_SELECTION
		elif self._trumpSelector.isComplete():
			if not self._round.isComplete():
				for playerId, hand in self._round.getHands().iteritems():
					if Round.MAX_HAND_SIZE < len(hand):
						return Sequence.STATE_DISCARD
				return Sequence.STATE_PLAYING_ROUND
			return Sequence.STATE_COMPLETE
		return Sequence.STATE_INVALID

	def selectTrump(self, player, trumpSuit):
		currentState = self.getState()
		if Sequence.STATE_TRUMP_SELECTION != currentState and Sequence.STATE_TRUMP_SELECTION_2 != currentState:
			raise game.GameStateException("Cannot select trump once trump selection is complete")
		self._trumpSelector.selectTrump(player, trumpSuit)
		if self._trumpSelector.isComplete():
			selectedTrump = self._trumpSelector.getSelectedTrump()
			if SUIT_NONE == selectedTrump and Sequence.STATE_TRUMP_SELECTION_FAILED != self.getState():
				self._trumpSelector.reset()
			else:
				self._round.setTrump(selectedTrump)

	def playCard(self, player, card):
		if Sequence.STATE_PLAYING_ROUND != self.getState():
			raise game.GameStateException("Can only play cards when in playing round state")
		self._round.playCard(player, card)

	def addCardToHand(self, player, card):
		if Sequence.STATE_TRUMP_SELECTION != self.getState():
			raise game.GameStateException("Cannot add a card to a player's hand except during first round of trump selection")
		self._round.addCardToHand(player, card)

	def discardCard(self, player, card):
		if Sequence.STATE_DISCARD != self.getState():
			raise game.GameStateException("Cannot discard when not in discard state")
		self._round.discardCard(player, card)

	def scoreCurrentRound(self, scoreTracker):
		scoreTracker.recordRoundScore(self._round, self._trumpSelector.getSelectingPlayerId())

	def getRound(self):
		return self._round

	def getTrumpSelector(self):
		return self._trumpSelector

	def getUpCard(self):
		if Sequence.STATE_TRUMP_SELECTION == self.getState():
			return self._upCard
		return None

class SequenceFactory(object):
	instance = None
	@classmethod
	def getInstance(cls):
		if None != cls.instance:
			return cls.instance
		return SequenceFactory()

	def buildSequence(self, players, hands, upCard=None):
		return Sequence.getInstance(players, hands, upCard)

class ScoreTracker(object):
	instance = None
	@classmethod
	def getInstance(cls, players, teams):
		if None != cls.instance:
			return cls.instance
		return ScoreTracker(players, teams)

	def __init__(self, players, teams):
		self._players = players
		self._teams = teams
		self._teamScores = [0, 0]

	def recordRoundScore(self, round, callingPlayerId):
		if not round.isComplete():
			raise game.GameStateException("Cannot score incomplete Round")
		teamTricks = [0, 0]
		for teamId in range(len(self._teams)):
			for playerId in self._teams[teamId]:
				teamTricks[teamId] += round.getScore(playerId)
		winningTeam = 0 if teamTricks[0] > teamTricks[1] else 1
		self._teamScores[winningTeam] += 1
		if winningTeam != self.getTeamIdFromPlayerId(callingPlayerId):
			self._teamScores[winningTeam] += 1
		elif HAND_SIZE <= teamTricks[winningTeam] and 0 >= teamTricks[(winningTeam + 1) % len(self._teams)]:
			self._teamScores[winningTeam] += 1

	def getTeamScore(self, teamId):
		return self._teamScores[teamId]

	def getTeamIdFromPlayerId(self, playerId):
		for teamId in range(len(self._teams)):
			for curId in self._teams[teamId]:
				if playerId == curId:
					return teamId

	def getTeams(self):
		return self._teams

class Game(object):
	instance = None
	@classmethod
	def getInstance(cls, players, teams):
		if None != cls.instance:
			return cls.instance
		return Game(players, ScoreTracker.getInstance(players, teams), SequenceFactory.getInstance())

	def __init__(self, players, scoreTracker, sequenceFactory):
		self._players = players
		self._scoreTracker = scoreTracker
		self._sequenceFactory = sequenceFactory
		self._curSequence = None
		self._prevSequence = None

	def startGame(self):
		self._buildNextSequence()

	def getSequence(self):
		return self._curSequence

	def selectTrump(self, player, suit):
		self._curSequence.selectTrump(player, suit)
		if Sequence.STATE_TRUMP_SELECTION_FAILED == self._curSequence.getState():
			self._advanceDealer()
			self._buildNextSequence()

	def playCard(self, player, card):
		self._curSequence.playCard(player, card)
		if Sequence.STATE_COMPLETE == self._curSequence.getState():
			self._scoreCurrentSequence()
			self._advanceDealer()
			self._buildNextSequence()

	def addCardToHand(self, player, card):
		self._curSequence.addCardToHand(player, card)

	def discardCard(self, player, card):
		self._curSequence.discardCard(player, card)

	def getSequenceState(self):
		return self._curSequence.getState()

	def getPlayers(self):
		return self._players

	def getTeamScore(self, teamId):
		return self._scoreTracker.getTeamScore(teamId)

	def getTeamFromPlayerId(self, playerId):
		return self._scoreTracker.getTeamIdFromPlayerId(playerId)

	def getTeamLists(self):
		return self._scoreTracker.getTeams()

	def getPreviousSequence(self):
		return self._prevSequence

	def _dealHands(self, deck):
		hands = {}
		for player in self._players:
			hands[player.playerId] = deck.deal(HAND_SIZE)
		return hands

	def _advanceDealer(self):
		self._players = self._players[1:] + [self._players[0]]

	def _scoreCurrentSequence(self):
		self._curSequence.scoreCurrentRound(self._scoreTracker)

	def _buildNextSequence(self):
		self._prevSequence = self._curSequence
		self._curSequence = None
		if not self._someTeamWon():
			deck = Deck.getInstance(MIN_4_PLAYER_CARD_VALUE, VALUE_ACE)
			deck.shuffle()
			hands = self._dealHands(deck)
			self._curSequence = self._sequenceFactory.buildSequence(self._players, hands, deck.peekTop())

	def _someTeamWon(self):
		return WINNING_SCORE <= self.getTeamScore(0) or WINNING_SCORE <= self.getTeamScore(1)
