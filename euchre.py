import random
import game

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

class Card(object):
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

class Trick(object):
	def __init__(self):
		self.playedCards = {}
		self.ledSuit = None

	def add(self, player, card):
		if None == self.ledSuit:
			self.ledSuit = card.suit
		if player.playerId in self.playedCards:
			raise game.GameRuleException("Player with id %s has already played a card in this trick" % player.playerId)
		self.playedCards[player.playerId] = card

	def isComplete(self):
		return len(self.playedCards) >= NUM_PLAYERS

class TrickEvaluator(object):
	def __init__(self, trump=SUIT_NONE):
		self.trumpSuit = trump

	def setTrump(self, trumpSuit):
		self.trumpSuit = trumpSuit

	def evaluateTrick(self, trick):
		highestTrumpValue = -1
		highestLedValue = -1
		highestTrumpCard = None
		highestLedCard = None
		highestTrumpId = None
		highestLedId = None
		for playerId, card in trick.playedCards.iteritems():
			cardSuit = card.suit
			cardValue = card.value
			if cardValue == VALUE_JACK:
				if cardSuit == self.trumpSuit:
					cardValue = VALUE_RIGHT_BOWER
				elif cardSuit % 2 == self.trumpSuit % 2:
					cardSuit = self.trumpSuit
					cardValue = VALUE_LEFT_BOWER
			if cardSuit == self.trumpSuit and cardValue > highestTrumpValue:
				highestTrumpValue = cardValue
				highestTrumpCard = card
				highestTrumpId = playerId
			if cardSuit == trick.ledSuit and cardValue > highestLedValue:
				highestLedValue = cardValue
				highestLedCard = card
				highestLedId = playerId

		if highestTrumpCard:
			return highestTrumpId
		if highestLedCard:
			return highestLedId
		return None

class Round(object):
	def __init__(self, turnTracker, trickEvaluator, players, hands):
		self.players = players
		self.hands = hands
		self.curTrick = None
		self.prevTricks = []
		self._scores = {}
		self._trickEvaluator = trickEvaluator
		self._turnTracker = turnTracker

	def startRound(self):
		self.curTrick = Trick()

	def playCard(self, player, card):
		if None == player or player.playerId not in self.hands:
			raise game.InvalidPlayerException("Player with id %s is not a member of this round" % (None if None == player else player.playerId))
		if card not in self.hands[player.playerId]:
			raise game.GameRuleException("Player with id %s does not have card %s in their hand" % (player.playerId, card))
		if self._turnTracker.getCurrentPlayerId() != player.playerId:
			raise game.GameRuleException("It is not player %s's turn, current player id is %s" % (player.playerId, self._turnTracker.getCurrentPlayerId()))

		self.hands[player.playerId].remove(card)
		self.curTrick.add(player, card)
		self._nextTurn()

		if self.curTrick.isComplete():
			self._nextTrick()

	def isComplete(self):
		return HAND_SIZE <= len(self.prevTricks)

	def getScore(self, playerId):
		if playerId in self._scores:
			return self._scores[playerId]
		return 0

	def _nextTrick(self):
		winner = self._trickEvaluator.evaluateTrick(self.curTrick)
		self._incrementScore(winner)
		self.prevTricks.append(self.curTrick)
		self.curTrick = Trick()
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
	def __init__(self, turnTracker, availableTrump=SUIT_NONE):
		self._turnTracker = turnTracker
		self._availableTrump = availableTrump
		self._selectedTrump = SUIT_NONE

	def getAvailableTrump(self):
		return self._availableTrump

	def getSelectedTrump(self):
		return self._selectedTrump

	def selectTrump(self, player, trumpSuit):
		if self._turnTracker.getCurrentPlayerId() != player.playerId:
			raise game.GameRuleException("Player %s cannot select the trump right now, it is player %s's turn" % (player.playerId, self._turnTracker.getCurrentPlayerId()))
		if SUIT_NONE != trumpSuit:
			if SUIT_NONE != self._availableTrump and self._availableTrump != trumpSuit:
				raise game.GameRuleException("Cannot choose suit %s as trump while only suit %s is available" % (trumpSuit, self._availableTrump))
			self._selectedTrump = trumpSuit
		self._turnTracker.advanceTurn()

	def isComplete(self):
		return SUIT_NONE != self._selectedTrump or 1 <= self._turnTracker.getAllTurnCount()

	def reset(self):
		self._turnTracker.reset()
		self._availableTrump = SUIT_NONE
		self._selectedTrump = SUIT_NONE

class Sequence(object):
	STATE_TRUMP_SELECTION = "STATE_TRUMP_SELECTION"
	STATE_PLAYING_ROUND = "STATE_PLAYING_ROUND"

	def __init__(self, trumpSelector, round, players):
		self._trumpSelector = trumpSelector
		self._round = round
		self._players = players

	def getState(self):
		if self._trumpSelector.isComplete() and None != self._trumpSelector.getSelectedTrump():
			return Sequence.STATE_PLAYING_ROUND
		return Sequence.STATE_TRUMP_SELECTION

class ScoreTracker(object):
	def __init__(self, players, teams):
		self._players = players
		self._teams = teams
		self._teamScores = {0:0, 1:0}

	def recordRoundScore(self, round, callingPlayerId):
		if not round.isComplete():
			raise game.GameStateException("Cannot score incomplete Round")
		teamTricks = {0:0, 1:0}
		for teamId, playerIds in self._teams.iteritems():
			for playerId in playerIds:
				teamTricks[teamId] += round.getScore(playerId)
		winningTeam = 0 if teamTricks[0] > teamTricks[1] else 1
		self._teamScores[winningTeam] += 1
		if winningTeam != self._getTeamIdFromPlayerId(callingPlayerId):
			self._teamScores[winningTeam] += 1
		elif HAND_SIZE <= teamTricks[winningTeam] and 0 >= teamTricks[(winningTeam + 1) % len(self._teams)]:
			self._teamScores[winningTeam] += 1

	def getTeamScore(self, teamId):
		return self._teamScores[teamId]

	def _getTeamIdFromPlayerId(self, playerId):
		for teamId, players in self._teams.iteritems():
			for curId in players:
				if playerId == curId:
					return teamId
