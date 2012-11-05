#!/usr/bin/env python
import testhelper
import unittest
import mock
import serializer
import game
import euchre
import random

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

class GameSerializerTest(testhelper.TestCase):
	def setUp(self):
		self.playerSerializer = testhelper.createSingletonMock(serializer.PlayerSerializer)
		self.scoreTrackerSerializer = testhelper.createSingletonMock(serializer.ScoreTrackerSerializer)
		self.sequenceSerializer = testhelper.createSingletonMock(serializer.SequenceSerializer)
		self.game = euchre.Game.getInstance([game.Player("1"), game.Player("2"), game.Player("3"), game.Player("4")], [["1", "2"], ["3", "4"]])
		self.testObj = serializer.GameSerializer.getInstance()

	def testSerializesGameCorrectly(self):
		self.playerSerializer.serialize.side_effect = ["1", "2", "3", "4"]
		self.scoreTrackerSerializer.serialize.return_value = "serialized score tracker"
		self.sequenceSerializer.serialize.return_value = "serialized sequence"
		data = self.testObj.serialize(self.game)
		self.assertEqual(["1", "2", "3", "4"], data["players"])
		self.assertEqual("serialized score tracker", data["scoreTracker"])
		self.assertEqual("serialized sequence", data["curSequence"])

	def testDeserializesGameCorrectly(self):
		players = [game.Player("6"), game.Player("7"), game.Player("8"), game.Player("9")]
		self.playerSerializer.deserialize.side_effect = players
		scoreTracker = testhelper.createSingletonMock(euchre.ScoreTracker)
		self.scoreTrackerSerializer.deserialize.return_value = scoreTracker
		sequence = testhelper.createSingletonMock(euchre.Sequence)
		self.sequenceSerializer.deserialize.return_value = sequence
		data = {"players" : [1, 2, 3, 4], "scoreTracker" : None, "curSequence" : None}
		self.game = self.testObj.deserialize(data)
		self.assertEqual(players, self.game._players)
		self.assertEqual(scoreTracker, self.game._scoreTracker)
		self.assertEqual(sequence, self.game._curSequence)
		self.sequenceSerializer.deserialize.assert_called_with(data["curSequence"], players)

class ScoreTrackerSerializerTest(testhelper.TestCase):
	def setUp(self):
		self.players = [game.Player("1"), game.Player("2"), game.Player("3"), game.Player("4")]
		self.teams = [["1", "2"], ["3", "4"]]
		self.scores = [3, 6]
		self.scoreTracker = euchre.ScoreTracker.getInstance(self.players, self.teams)
		self.scoreTracker._scores = self.scores
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
		self.assertEqual(obj._scores, self.scores)

class SequenceSerializerTest(testhelper.TestCase):
	def setUp(self):
		self.trumpSelector = testhelper.createMock(euchre.TrumpSelector)
		self.round = testhelper.createMock(euchre.Round)
		self.sequence = euchre.Sequence(self.trumpSelector, self.round)
		self.trumpSelectorSerializer = testhelper.createSingletonMock(serializer.TrumpSelectorSerializer)
		self.roundSerializer = testhelper.createSingletonMock(serializer.RoundSerializer)
		self.testObj = serializer.SequenceSerializer.getInstance()

	def testSerializesSequenceCorrectly(self):
		expectedTrumpSelector = "a trump selector"
		expectedRound = "a round"
		self.trumpSelectorSerializer.serialize.return_value = expectedTrumpSelector
		self.roundSerializer.serialize.return_value = expectedRound
		data = self.testObj.serialize(self.sequence)
		self.assertEqual(expectedTrumpSelector, data["trumpSelector"])
		self.assertEqual(expectedRound, data["round"])

	def testDeserializesSequenceCorrectly(self):
		players = "some players"
		data = {"trumpSelector" : "a trump selector", "round" : "a round"}
		self.trumpSelectorSerializer.deserialize.return_value = self.trumpSelector
		self.roundSerializer.deserialize.return_value = self.round
		obj = self.testObj.deserialize(data, players)
		self.assertEqual(self.trumpSelector, obj._trumpSelector)
		self.assertEqual(self.round, obj._round)
		self.trumpSelectorSerializer.deserialize.assert_called_with(data["trumpSelector"], players)
		self.roundSerializer.deserialize.assert_called_with(data["round"], players)

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
		self.turnTrackerSerializer.serialize.return_value = expectedTurnTracker
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
		data = {"turnTracker" : "a turn tracker", "availableTrump" : self.availableTrump, "selectingPlayerId" : self.selectingPlayerId}
		self.turnTrackerSerializer.deserialize.return_value = self.turnTracker
		obj = self.testObj.deserialize(data, players)
		self.assertEqual(self.turnTracker, obj._turnTracker)
		self.assertEqual(self.availableTrump, obj._availableTrump)
		self.assertEqual(self.selectingPlayerId, obj._selectingPlayerId)
		self.turnTrackerSerializer.deserialize.assert_called_with(data["turnTracker"], players)

	def testDeserializeSetsCorrectValueForSelectingPlayerIdOfEmptyString(self):
		players = "some players"
		data = {"turnTracker" : "a turn tracker", "availableTrump" : self.availableTrump, "selectingPlayerId" : ""}
		obj = self.testObj.deserialize(data, players)
		self.assertEqual(None, obj._selectingPlayerId)

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
		expectedHands = {"1" : ["card 1", "card 2"], "2" : ["card 3", "card 4"]}
		cardSerializerResult = []
		cardSerializerResult.extend(expectedHands["1"])
		cardSerializerResult.extend(expectedHands["2"])
		self.cardSerializer.serialize.side_effect = cardSerializerResult
		expectedTurnTracker = "a turn tracker"
		self.turnTrackerSerializer.serialize.return_value = expectedTurnTracker
		expectedTrickEvaluator = "a trick evaluator"
		self.trickEvaluatorSerializer.serialize.return_value = expectedTrickEvaluator
		curTrick = testhelper.createMock(euchre.Trick)
		self.round._curTrick = curTrick
		prevTricks = [testhelper.createMock(euchre.Trick), testhelper.createMock(euchre.Trick)]
		self.round._prevTricks = prevTricks
		expectedTricks = {curTrick : "trick 1", prevTricks[0] : "trick 2", prevTricks[1] : "trick 3"}
		self.trickSerializer.serialize.side_effect = lambda t : expectedTricks[t]
		scores = {"1" : 0, "2" : 5}
		self.round._scores = scores

		data = self.testObj.serialize(self.round)

		self.assertEqual(expectedTurnTracker, data["turnTracker"])
		self.assertEqual(expectedTrickEvaluator, data["trickEvaluator"])
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
		self.turnTrackerSerializer.deserialize.return_value = self.turnTracker
		self.trickEvaluatorSerializer.deserialize.return_value = self.trickEvaluator

		expectedCards = {}
		for playerId, hand in hands.iteritems():
			for card in hand:
				expectedCards[card] = self._randomCard()
		self.cardSerializer.deserialize.side_effect = lambda c: expectedCards[c]

		expectedTricks = {curTrick : testhelper.createMock(euchre.Trick)}
		for trick in prevTricks:
			expectedTricks[trick] = testhelper.createMock(euchre.Trick)
		self.trickSerializer.deserialize.side_effect = lambda t: expectedTricks[t]

		obj = self.testObj.deserialize(data, players)

		self.assertEqual(self.turnTracker, obj._turnTracker)
		self.turnTrackerSerializer.deserialize.assert_called_with(serializedTurnTracker, players)
		self.assertEqual(self.trickEvaluator, obj._trickEvaluator)
		for playerId, hand in hands.iteritems():
			for i in range(len(hand)):
				self.assertEqual(expectedCards[hand[i]], obj.hands[playerId][i])
		self.assertEqual(expectedTricks[curTrick], obj.curTrick)
		for i in range(len(prevTricks)):
			self.assertEqual(expectedTricks[prevTricks[i]], obj.prevTricks[i])
		for playerId, score in scores.iteritems():
			self.assertEqual(score, obj._scores[playerId])

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

class TrickSerializerTest(testhelper.TestCase):
	def setUp(self):
		self.cardSerializer = testhelper.createSingletonMock(serializer.CardSerializer)
		self.testObj = serializer.TrickSerializer.getInstance()

	def testSerializesTrickCorrectly(self):
		expectedLedSuit = random.randint(1, euchre.NUM_SUITS)
		playedCards = {"1" : self._randomCard(), "2" : self._randomCard()}
		expectedCards = {playedCards["1"] : "card 1", playedCards["2"] : "card 2"}
		self.cardSerializer.serialize.side_effect = lambda c: expectedCards[c]
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
			playedCards[card] = self._randomCard()
		self.cardSerializer.deserialize.side_effect = lambda c: playedCards[c]

		obj = self.testObj.deserialize(data)

		self.assertEqual(expectedLedSuit, obj.ledSuit)
		for playerId, card in expectedPlayedCards.iteritems():
			self.assertEqual(playedCards[card], obj.playedCards[playerId])

	def _randomCard(self):
		suit = random.randint(1, euchre.NUM_SUITS)
		value = random.randint(euchre.VALUE_MIN, euchre.VALUE_ACE)
		return euchre.Card(suit, value)

if __name__ == "__main__":
	unittest.main()
