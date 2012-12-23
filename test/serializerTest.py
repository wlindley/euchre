#!/usr/bin/env python
import testhelper
import unittest
import random
import json
from mockito import *

from src import serializer
from src import game
from src import euchre

class PlayerSerializerTest(testhelper.TestCase):
	def setUp(self):
		super(PlayerSerializerTest, self).setUp()
		self.testObj = serializer.PlayerSerializer.getInstance()
		self.playerId = "123"

	def testSerializesPlayerCorrectly(self):
		player = game.Player(self.playerId)
		data = self.testObj.serialize(player)
		self.assertEqual(self.playerId, data["playerId"])

	def testDeserializesPlayerCorrectly(self):
		data = {"playerId" : self.playerId}
		player = self.testObj.deserialize(data)
		self.assertEqual(self.playerId, player.playerId)

	def testHandlesNoneGracefully(self):
		self.assertEqual(None, self.testObj.serialize(None))
		self.assertEqual(None, self.testObj.deserialize(None))

class GameSerializerTest(testhelper.TestCase):
	def setUp(self):
		self.playerSerializer = testhelper.createSingletonMock(serializer.PlayerSerializer)
		self.scoreTrackerSerializer = testhelper.createSingletonMock(serializer.ScoreTrackerSerializer)
		self.sequenceSerializer = testhelper.createSingletonMock(serializer.SequenceSerializer)
		self.players = [game.Player("1"), game.Player("2"), game.Player("3"), game.Player("4")]
		self.scoreTracker = testhelper.createSingletonMock(euchre.ScoreTracker)
		self.sequence = testhelper.createSingletonMock(euchre.Sequence)
		self.game = euchre.Game.getInstance(self.players, [["1", "2"], ["3", "4"]])
		self.testObj = serializer.GameSerializer.getInstance()

	def testSerializesGameCorrectly(self):
		self.game.startGame()
		for player in self.players:
			when(self.playerSerializer).serialize(player).thenReturn(player.playerId)
		serializedScoreTracker = "serialized score tracker"
		when(self.scoreTrackerSerializer).serialize(self.scoreTracker).thenReturn(serializedScoreTracker)
		serializedSequence = "serialized sequence"
		when(self.sequenceSerializer).serialize(self.sequence).thenReturn(serializedSequence)
		data = self.testObj.serialize(self.game)
		self.assertEqual(["1", "2", "3", "4"], data["players"])
		self.assertEqual(serializedScoreTracker, data["scoreTracker"])
		self.assertEqual(serializedSequence, data["curSequence"])

	def testDeserializesGameCorrectly(self):
		for player in self.players:
			when(self.playerSerializer).deserialize(player.playerId).thenReturn(player)
		serializedScoreTracker = "a serialized score tracker"
		when(self.scoreTrackerSerializer).deserialize(serializedScoreTracker, self.players).thenReturn(self.scoreTracker)
		serializedSequence = "a serialized sequence"
		when(self.sequenceSerializer).deserialize(serializedSequence, self.players).thenReturn(self.sequence)
		data = {"players" : ["1", "2", "3", "4"], "scoreTracker" : serializedScoreTracker, "curSequence" : serializedSequence}
		self.game = self.testObj.deserialize(data)
		self.assertEqual(self.players, self.game._players)
		self.assertEqual(self.scoreTracker, self.game._scoreTracker)
		self.assertEqual(self.sequence, self.game._curSequence)
		verify(self.sequenceSerializer).deserialize(data["curSequence"], self.players)

	def testHandlesNoneGracefully(self):
		self.assertEqual(None, self.testObj.serialize(None))
		self.assertEqual(None, self.testObj.deserialize(None))

class ScoreTrackerSerializerTest(testhelper.TestCase):
	def setUp(self):
		self.players = [game.Player("1"), game.Player("2"), game.Player("3"), game.Player("4")]
		self.teams = [["1", "2"], ["3", "4"]]
		self.scores = [3, 6]
		self.scoreTracker = euchre.ScoreTracker.getInstance(self.players, self.teams)
		self.scoreTracker._teamScores = self.scores
		self.testObj = serializer.ScoreTrackerSerializer.getInstance()

	def testSerializesScoreTrackerCorrectly(self):
		data = self.testObj.serialize(self.scoreTracker)
		self.assertEqual(self.teams, data["teams"])
		self.assertEqual(self.scores, data["scores"])

	def testDeserializesScoreTrackerCorrectly(self):
		data = {"teams" : self.teams, "scores" : self.scores}
		obj = self.testObj.deserialize(data, self.players)
		self.assertEqual(obj._players, self.players)
		self.assertEqual(obj._teams, self.teams)
		self.assertEqual(obj._teamScores, self.scores)

	def testHandlesNoneGracefully(self):
		self.assertEqual(None, self.testObj.serialize(None))
		self.assertEqual(None, self.testObj.deserialize(None, "some players"))

class SequenceSerializerTest(testhelper.TestCase):
	def setUp(self):
		self.trumpSelector = testhelper.createMock(euchre.TrumpSelector)
		self.round = testhelper.createMock(euchre.Round)
		self.upCard = euchre.Card(euchre.SUIT_DIAMONDS, euchre.VALUE_KING)
		self.sequence = euchre.Sequence(self.trumpSelector, self.round, self.upCard)
		self.trumpSelectorSerializer = testhelper.createSingletonMock(serializer.TrumpSelectorSerializer)
		self.roundSerializer = testhelper.createSingletonMock(serializer.RoundSerializer)
		self.cardSerializer = testhelper.createSingletonMock(serializer.CardSerializer)
		self.testObj = serializer.SequenceSerializer.getInstance()

	def testSerializesSequenceCorrectly(self):
		expectedTrumpSelector = "a trump selector"
		expectedRound = "a round"
		expectedCard = "a card"
		when(self.trumpSelectorSerializer).serialize(self.trumpSelector).thenReturn(expectedTrumpSelector)
		when(self.roundSerializer).serialize(self.round).thenReturn(expectedRound)
		when(self.cardSerializer).serialize(self.upCard).thenReturn(expectedCard)
		data = self.testObj.serialize(self.sequence)
		self.assertEqual(expectedTrumpSelector, data["trumpSelector"])
		self.assertEqual(expectedRound, data["round"])
		self.assertEqual(expectedCard, data["upCard"])

	def testDeserializesSequenceCorrectly(self):
		players = "some players"
		serializedTrumpSelector = "a trump selector"
		serializedRound = "a round"
		serializedCard = "a card"
		data = {"trumpSelector" : serializedTrumpSelector, "round" : serializedRound, "upCard" : serializedCard}
		when(self.trumpSelectorSerializer).deserialize(serializedTrumpSelector, players).thenReturn(self.trumpSelector)
		when(self.roundSerializer).deserialize(serializedRound, players).thenReturn(self.round)
		when(self.cardSerializer).deserialize(serializedCard).thenReturn(self.upCard)
		obj = self.testObj.deserialize(data, players)
		self.assertEqual(self.trumpSelector, obj._trumpSelector)
		self.assertEqual(self.round, obj._round)
		self.assertEqual(self.upCard, obj._upCard)
		verify(self.trumpSelectorSerializer).deserialize(data["trumpSelector"], players)
		verify(self.roundSerializer).deserialize(data["round"], players)

	def testHandlesNoneGracefully(self):
		self.assertEqual(None, self.testObj.serialize(None))
		self.assertEqual(None, self.testObj.deserialize(None, "some players"))

class TrumpSelectorSerializerTest(testhelper.TestCase):
	def setUp(self):
		self.turnTracker = testhelper.createMock(game.TurnTracker)
		self.availableTrump = euchre.SUIT_HEARTS
		self.selectingPlayerId = "123456"
		self.trumpSelector = euchre.TrumpSelector(self.turnTracker, self.availableTrump)
		self.turnTrackerSerializer = testhelper.createSingletonMock(serializer.TurnTrackerSerializer)
		self.testObj = serializer.TrumpSelectorSerializer.getInstance()

	def testSerializesTrumpSelectorCorrectly(self):
		expectedTurnTracker = "a turn tracker"
		when(self.turnTrackerSerializer).serialize(self.turnTracker).thenReturn(expectedTurnTracker)
		self.trumpSelector._selectingPlayerId = self.selectingPlayerId
		data = self.testObj.serialize(self.trumpSelector)
		self.assertEqual(expectedTurnTracker, data["turnTracker"])
		self.assertEqual(self.availableTrump, data["availableTrump"])
		self.assertEqual(self.selectingPlayerId, data["selectingPlayerId"])

	def testSerializeUsesCorrectValueWhenSelectingPlayerIdIsNone(self):
		data = self.testObj.serialize(self.trumpSelector)
		self.assertEqual("", data["selectingPlayerId"])

	def testDeserializesTrumpSelectorCorrectly(self):
		players = "some players"
		serializedTurnTracker = "a turnTracker"
		data = {"turnTracker" : serializedTurnTracker, "availableTrump" : self.availableTrump, "selectingPlayerId" : self.selectingPlayerId}
		when(self.turnTrackerSerializer).deserialize(serializedTurnTracker, players).thenReturn(self.turnTracker)
		obj = self.testObj.deserialize(data, players)
		self.assertEqual(self.turnTracker, obj._turnTracker)
		self.assertEqual(self.availableTrump, obj._availableTrump)
		self.assertEqual(self.selectingPlayerId, obj._selectingPlayerId)
		verify(self.turnTrackerSerializer).deserialize(data["turnTracker"], players)

	def testDeserializeSetsCorrectValueForSelectingPlayerIdOfEmptyString(self):
		players = "some players"
		data = {"turnTracker" : "a turn tracker", "availableTrump" : self.availableTrump, "selectingPlayerId" : ""}
		obj = self.testObj.deserialize(data, players)
		self.assertEqual(None, obj._selectingPlayerId)

	def testHandlesNoneGracefully(self):
		self.assertEqual(None, self.testObj.serialize(None))
		self.assertEqual(None, self.testObj.deserialize(None, "some players"))

class TurnTrackerSerializerTest(testhelper.TestCase):
	def setUp(self):
		self.players = [game.Player("1"), game.Player("2"), game.Player("3"), game.Player("4")]
		self.currentTurn = 2
		self.allTurnCount = 0
		self.turnTracker = game.TurnTracker.getInstance(self.players)
		self.turnTracker._currentIndex = self.currentTurn
		self.turnTracker._allTurnCount = self.allTurnCount
		self.testObj = serializer.TurnTrackerSerializer.getInstance()

	def testSerializesTurnTrackerCorrectly(self):
		data = self.testObj.serialize(self.turnTracker)
		self.assertEqual(self.currentTurn, data["currentIndex"])
		self.assertEqual(self.allTurnCount, data["allTurnCount"])

	def testDeserializesTurnTrackerCorrectly(self):
		data = {"currentIndex" : self.currentTurn, "allTurnCount" : self.allTurnCount}
		obj = self.testObj.deserialize(data, self.players)
		self.assertEquals(self.currentTurn, obj._currentIndex)
		self.assertEquals(self.allTurnCount, obj._allTurnCount)
		for i in range(len(self.players)):
			self.assertEquals(self.players[i], obj._players[i])

	def testHandlesNoneGracefully(self):
		self.assertEqual(None, self.testObj.serialize(None))
		self.assertEqual(None, self.testObj.deserialize(None, "some players"))

class RoundSerializerTest(testhelper.TestCase):
	def setUp(self):
		self.hands = {"1" : [self._randomCard(), self._randomCard()], "2" : [self._randomCard(), self._randomCard()]}
		self.trickEvaluator = testhelper.createMock(euchre.TrickEvaluator)
		self.trickEvaluatorSerializer = testhelper.createSingletonMock(serializer.TrickEvaluatorSerializer)
		self.turnTracker = testhelper.createMock(game.TurnTracker)
		self.turnTrackerSerializer = testhelper.createSingletonMock(serializer.TurnTrackerSerializer)
		self.trickSerializer = testhelper.createSingletonMock(serializer.TrickSerializer)
		self.cardSerializer = testhelper.createSingletonMock(serializer.CardSerializer)
		self.round = euchre.Round(self.turnTracker, self.trickEvaluator, self.hands)
		self.testObj = serializer.RoundSerializer.getInstance()

	def _randomCard(self):
		suit = random.randint(1, euchre.NUM_SUITS)
		value = random.randint(euchre.VALUE_MIN, euchre.VALUE_ACE)
		return euchre.Card(suit, value)

	def testSerializesRoundCorrectly(self):
		expectedHands = {}
		i = 0
		for playerId, hand in self.hands.iteritems():
			expectedHands[playerId] = []
			for card in hand:
				serializedCard = "card %d" % i
				expectedHands[playerId].append(serializedCard)
				when(self.cardSerializer).serialize(card).thenReturn(serializedCard)
				i += 1
		expectedTurnTracker = "a turn tracker"
		when(self.turnTrackerSerializer).serialize(self.turnTracker).thenReturn(expectedTurnTracker)
		expectedTrickEvaluator = "a trick evaluator"
		when(self.trickEvaluatorSerializer).serialize(self.trickEvaluator).thenReturn(expectedTrickEvaluator)
		curTrick = testhelper.createMock(euchre.Trick)
		self.round.curTrick = curTrick
		prevTricks = [testhelper.createMock(euchre.Trick), testhelper.createMock(euchre.Trick)]
		self.round.prevTricks = prevTricks
		expectedTricks = {curTrick : "trick 1", prevTricks[0] : "trick 2", prevTricks[1] : "trick 3"}
		when(self.trickSerializer).serialize(curTrick).thenReturn("trick 1")
		when(self.trickSerializer).serialize(prevTricks[0]).thenReturn("trick 2")
		when(self.trickSerializer).serialize(prevTricks[1]).thenReturn("trick 3")
		scores = {"1" : 0, "2" : 5}
		self.round._scores = scores

		data = self.testObj.serialize(self.round)

		self.assertEqual(expectedTurnTracker, data["turnTracker"])
		self.assertEqual(expectedTrickEvaluator, data["trickEvaluator"])
		print data["hands"]
		for playerId in expectedHands:
			for i in range(len(expectedHands[playerId])):
				self.assertEqual(expectedHands[playerId][i], data["hands"][playerId][i])
		self.assertEqual(expectedTricks[curTrick], data["curTrick"])
		for i in range(len(prevTricks)):
			self.assertEqual(expectedTricks[prevTricks[i]], data["prevTricks"][i])
		for playerId, score in scores.iteritems():
			self.assertEqual(score, data["scores"][playerId])

	def testDeserializesRoundCorrectly(self):
		players = "some players"
		serializedTurnTracker = "a turn tracker"
		serializedTrickEvaluator = "a trick evaluator"
		hands = {"1" : ["card 1", "card 2"], "2" : ["card 3", "card 4"]}
		curTrick = "trick 1"
		prevTricks = ["trick 2", "trick 3"]
		scores = {"1" : 3, "2" : 2}
		data = {"turnTracker" : serializedTurnTracker,
				"trickEvaluator" : serializedTrickEvaluator,
				"hands" : hands,
				"curTrick" : curTrick,
				"prevTricks" : prevTricks,
				"scores" : scores}
		when(self.turnTrackerSerializer).deserialize(serializedTurnTracker, players).thenReturn(self.turnTracker)
		when(self.trickEvaluatorSerializer).deserialize(serializedTrickEvaluator).thenReturn(self.trickEvaluator)

		expectedCards = {}
		for playerId, hand in hands.iteritems():
			for card in hand:
				deserializedCard = self._randomCard()
				when(self.cardSerializer).deserialize(card).thenReturn(deserializedCard)
				expectedCards[card] = deserializedCard

		expectedTricks = {curTrick : testhelper.createMock(euchre.Trick)}
		when(self.trickSerializer).deserialize(curTrick).thenReturn(expectedTricks[curTrick])
		for trick in prevTricks:
			deserializedTrick = testhelper.createMock(euchre.Trick)
			expectedTricks[trick] = deserializedTrick
			when(self.trickSerializer).deserialize(trick).thenReturn(deserializedTrick)

		obj = self.testObj.deserialize(data, players)

		self.assertEqual(self.turnTracker, obj._turnTracker)
		verify(self.turnTrackerSerializer).deserialize(serializedTurnTracker, players)
		self.assertEqual(self.trickEvaluator, obj._trickEvaluator)
		for playerId, hand in hands.iteritems():
			for i in range(len(hand)):
				self.assertEqual(expectedCards[hand[i]], obj.hands[playerId][i])
		self.assertEqual(expectedTricks[curTrick], obj.curTrick)
		for i in range(len(prevTricks)):
			self.assertEqual(expectedTricks[prevTricks[i]], obj.prevTricks[i])
		for playerId, score in scores.iteritems():
			self.assertEqual(score, obj._scores[playerId])

	def testHandlesNoneGracefully(self):
		self.assertEqual(None, self.testObj.serialize(None))
		self.assertEqual(None, self.testObj.deserialize(None, "some players"))

class TrickEvaluatorSerializerTest(testhelper.TestCase):
	def setUp(self):
		self.testObj = serializer.TrickEvaluatorSerializer.getInstance()

	def testSerializesTrickEvaluatorCorrectly(self):
		trumpSuit = random.randint(1, euchre.NUM_SUITS)
		trickEvaluator = euchre.TrickEvaluator(trumpSuit)
		data = self.testObj.serialize(trickEvaluator)
		self.assertEqual(trumpSuit, data["trumpSuit"])

	def testDeserializesTrickEvaluatorCorrectly(self):
		expectedTrumpSuit = random.randint(1, euchre.NUM_SUITS)
		data = {"trumpSuit" : expectedTrumpSuit}
		obj = self.testObj.deserialize(data)
		self.assertEqual(expectedTrumpSuit, obj._trumpSuit)

	def testHandlesNoneGracefully(self):
		self.assertEqual(None, self.testObj.serialize(None))
		self.assertEqual(None, self.testObj.deserialize(None))

class TrickSerializerTest(testhelper.TestCase):
	def setUp(self):
		self.cardSerializer = testhelper.createSingletonMock(serializer.CardSerializer)
		self.testObj = serializer.TrickSerializer.getInstance()

	def testSerializesTrickCorrectly(self):
		expectedLedSuit = random.randint(1, euchre.NUM_SUITS)
		playedCards = {"1" : self._randomCard(), "2" : self._randomCard()}
		expectedCards = {playedCards["1"] : "card 1", playedCards["2"] : "card 2"}
		for key, val in expectedCards.iteritems():
			when(self.cardSerializer).serialize(key).thenReturn(val)
		trick = euchre.Trick()
		trick.ledSuit = expectedLedSuit
		trick.playedCards = playedCards

		data = self.testObj.serialize(trick)

		self.assertEqual(expectedLedSuit, data["ledSuit"])
		for playerId, card in playedCards.iteritems():
			self.assertEqual(expectedCards[card], data["playedCards"][playerId])

	def testDeserializesTrickCorrectly(self):
		expectedLedSuit = random.randint(1, euchre.NUM_SUITS)
		expectedPlayedCards = {"1" : "card 1", "2" : "card 2"}
		data = {"ledSuit" : expectedLedSuit, "playedCards" : expectedPlayedCards}
		playedCards = {}
		for playerId, card in expectedPlayedCards.iteritems():
			deserializedCard = self._randomCard()
			playedCards[card] = deserializedCard
			when(self.cardSerializer).deserialize(card).thenReturn(deserializedCard)

		obj = self.testObj.deserialize(data)

		self.assertEqual(expectedLedSuit, obj.ledSuit)
		for playerId, card in expectedPlayedCards.iteritems():
			self.assertEqual(playedCards[card], obj.playedCards[playerId])

	def testHandlesNoneGracefully(self):
		self.assertEqual(None, self.testObj.serialize(None))
		self.assertEqual(None, self.testObj.deserialize(None))

	def _randomCard(self):
		suit = random.randint(1, euchre.NUM_SUITS)
		value = random.randint(euchre.VALUE_MIN, euchre.VALUE_ACE)
		return euchre.Card(suit, value)

class CardSerializerTest(testhelper.TestCase):
	def setUp(self):
		self.testObj = serializer.CardSerializer.getInstance()

	def testSerializesCardCorrectly(self):
		expectedSuit = random.randint(1, euchre.NUM_SUITS)
		expectedValue = random.randint(euchre.VALUE_MIN, euchre.VALUE_ACE)
		card = euchre.Card.getInstance(expectedSuit, expectedValue)
		data = self.testObj.serialize(card)
		self.assertEqual(expectedSuit, data["suit"])
		self.assertEqual(expectedValue, data["value"])

	def testDeserializesCardCorrectly(self):
		expectedSuit = random.randint(1, euchre.NUM_SUITS)
		expectedValue = random.randint(euchre.VALUE_MIN, euchre.VALUE_ACE)
		data = {"suit" : expectedSuit, "value" : expectedValue}
		obj = self.testObj.deserialize(data)
		self.assertEqual(expectedSuit, obj.suit)
		self.assertEqual(expectedValue, obj.value)

	def testHandlesNoneGracefully(self):
		self.assertEqual(None, self.testObj.serialize(None))
		self.assertEqual(None, self.testObj.deserialize(None))

class SerializerAcceptanceTest(testhelper.TestCase):
	def setUp(self):
		self.players = [game.Player("1"), game.Player("2"), game.Player("3"), game.Player("4")]
		self.teams = {0 : [self.players[0].playerId, self.players[1].playerId], 1 : [self.players[2].playerId, self.players[3].playerId]}
		self.gameSerializer = serializer.GameSerializer.getInstance()

	def testCanSerializeAndDeserializeGameWithoutError(self):
		game = euchre.Game.getInstance(self.players, self.teams)
		game.startGame()
		serialized = self.gameSerializer.serialize(game)
		deserialized = self.gameSerializer.deserialize(serialized)

if __name__ == "__main__":
	unittest.main()
