#!/usr/bin/env python
import testhelper
import unittest
import mock
import serializer
import game
import euchre

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
		data = {"trumpSelector" : "a trump selector", "round" : "a round"}
		self.trumpSelectorSerializer.deserialize.return_value = self.trumpSelector
		self.roundSerializer.deserialize.return_value = self.round
		obj = self.testObj.deserialize(data)
		self.assertEqual(self.trumpSelector, obj._trumpSelector)
		self.assertEqual(self.round, obj._round)

if __name__ == "__main__":
	unittest.main()
