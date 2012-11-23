#!/usr/bin/env python
import testhelper
import unittest
import mock
import game

class PlayerTest(testhelper.TestCase):
	def setUp(self):
		super(PlayerTest, self).setUp()
		self.player1 = game.Player("123")
		self.player2 = game.Player("456")

	def testPlayerEquality(self):
		player3 = game.Player("123")
		self.assertEqual(player3, self.player1)
		self.assertNotEqual(self.player2, self.player1)

class TurnTrackerTest(testhelper.TestCase):
	def setUp(self):
		super(TurnTrackerTest, self).setUp()
		self.players = [game.Player("1"), game.Player("2"), game.Player("3"), game.Player("4")]
		self.turnTracker = game.TurnTracker(self.players)

	def testDefaultsToFirstPlayersTurn(self):
		self.assertEqual(self.players[0].playerId, self.turnTracker.getCurrentPlayerId())

	def testAdvanceTurnMakesItNextPlayersTurn(self):
		self.turnTracker.advanceTurn()
		self.assertEqual(self.players[1].playerId, self.turnTracker.getCurrentPlayerId())

	def testAdvanceTurnWrapsBackToTheFirstPlayerAfterGoingThroughAllPlayers(self):
		for player in self.players:
			self.turnTracker.advanceTurn()
		self.assertEqual(self.players[0].playerId, self.turnTracker.getCurrentPlayerId())

	def testSetTurnByPlayerIdSetsItToCorrectPlayersTurn(self):
		playerId = "3"
		self.turnTracker.setTurnByPlayerId(playerId)
		self.assertEqual(2, self.turnTracker._currentIndex)
		self.assertEqual(playerId, self.turnTracker.getCurrentPlayerId())

	def testGetAllTurnCountReturnsCorrectNumberOfFullTurns(self):
		for player in self.players:
			self.assertEqual(0, self.turnTracker.getAllTurnCount())
			self.turnTracker.advanceTurn()
		self.assertEqual(1, self.turnTracker.getAllTurnCount())
		self.turnTracker.advanceTurn()
		self.assertEqual(1, self.turnTracker.getAllTurnCount())

	def testResetResetsStateButLeavesPlayerList(self):
		for player in self.players:
			self.turnTracker.advanceTurn()
		self.turnTracker.reset()
		self.assertEqual(self.players[0].playerId, self.turnTracker.getCurrentPlayerId())
		self.assertEqual(0, self.turnTracker.getAllTurnCount())

if __name__ == "__main__":
	unittest.main()
