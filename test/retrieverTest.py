#!/usr/bin/env python
import testhelper
import json
from mockito import *

from src import euchre
from src import model
from src import game
from src import retriever

class DealerRetrieverTest(testhelper.TestCase):
	def setUp(self):
		self.testObj = retriever.DealerRetriever.getInstance()

	def testRetrieveDealerReturnsCorrectResult(self):
		gameObj = testhelper.createMock(euchre.Game)
		players = [game.Player("1"), game.Player("2"), game.Player("3"), game.Player("4")]
		when(gameObj).getPlayers().thenReturn(players)

		actualResult = self.testObj.retrieveDealer(gameObj)
		self.assertEqual(players[0].playerId, actualResult)
