#!/usr/bin/env python
import unittest
import mock
import game

class TurnTrackerTest(unittest.TestCase):
	def setUp(self):
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

if __name__ == "__main__":
	unittest.main()
