#!/usr/bin/env python
from google.appengine.ext import ndb
import testhelper
from mockito import *

from src import filter
from src import model

class BaseFilterTest(testhelper.TestCase):
	def _buildTestObj(self):
		self.testObj = filter.BaseFilter.getInstance()

	def setUp(self):
		self._buildTestObj()

	def testFilterItemReturnsTrue(self):
		self.assertTrue(self.testObj.filterItem(None))

	def testFilterListReturnsAllItemsThatFilterItemReturnsTrueFor(self):
		items = [1, 2, "abc", None]
		result = self.testObj.filterList(items)
		self.assertEqual(items, result)

class PlayerHasNotRemovedGameModelFilterTest(testhelper.TestCase):
	def _buildTestObj(self):
		self.testObj = filter.PlayerHasNotRemovedGameModelFilter.getInstance(self.playerId)

	def setUp(self):
		self.playerId = "asd123"

		self.gameModel = testhelper.createMock(model.GameModel)
		self.gameModel.readyToRemove = []

		self._buildTestObj()

	def testGameModelWithoutPlayerIdInReadyToRemoveListPasses(self):
		self.assertTrue(self.testObj.filterItem(self.gameModel))

	def testGameModelWithPlayerIdInReadyToRemoveListFails(self):
		self.gameModel.readyToRemove = [self.playerId]
		self.assertFalse(self.testObj.filterItem(self.gameModel))

	def testFilterListOnlyReturnsItemsGameModelsWithoutPlayerId(self):
		gameModel2 = testhelper.createMock(model.GameModel)
		gameModel2.readyToRemove = [self.playerId]

		result = self.testObj.filterList([self.gameModel, gameModel2])

		self.assertEqual([self.gameModel], result)