#!/usr/bin/env python
import testhelper
import model

class GameModelFactoryTest(testhelper.TestCase):
	def setUp(self):
		self.testObj = model.GameModelFactory.getInstance()

	def testCreateReturnsGameModelWithGivenId(self):
		gameId = 5428
		result = self.testObj.create(gameId)
		self.assertTrue(isinstance(result, model.GameModel))
		self.assertEqual(gameId, result.gameId)
