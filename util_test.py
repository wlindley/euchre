#!/usr/bin/env python
from google.appengine.ext import ndb
import mock
import testhelper
import util
import model

class RequestDataAccessorTest(testhelper.TestCase):
	def setUp(self):
		self.request = mock.MagicMock()
		self.request.get = mock.MagicMock()
		self.testObj = util.RequestDataAccessor.getInstance(self.request)

	def testGetPassesThroughToRequest(self):
		params = "some key"
		expectedResult = "some data"
		self.request.get.side_effect = lambda p: expectedResult if params == p else mock.DEFAULT
		result = self.testObj.get(params)
		self.assertEqual(expectedResult, result)

class ResponseWriterTest(testhelper.TestCase):
	def setUp(self):
		self.response = mock.MagicMock()
		self.response.write = mock.MagicMock()
		self.testObj = util.ResponseWriter.getInstance(self.response)

	def testWritePassesThroughToResponse(self):
		params = "some response"
		self.testObj.write(params)
		self.response.write.assert_called_with(params)

class GameIdTrackerTest(testhelper.TestCase):
	def setUp(self):
		self.key = testhelper.createMock(ndb.Key)
		self.model = testhelper.createMock(model.GameIdModel)
		self.testObj = util.GameIdTracker.getInstance()
		self.testObj._getGameIdKey = mock.MagicMock()
		self.testObj._getGameIdKey.return_value = self.key
		self.key.get.return_value = self.model

	def testGetsAndIncrementsValue(self):
		expectedGameId = 100
		self.model.nextGameId = expectedGameId
		result = self.testObj.getGameId()
		self.assertEqual(expectedGameId, result)
		self.assertEqual(expectedGameId + 1, self.model.nextGameId)
		self.assertTrue(self.model.put.called)

class GameModelFactoryTest(testhelper.TestCase):
	def setUp(self):
		self.testObj = util.GameModelFactory.getInstance()

	def testCreateReturnsGameModelWithGivenId(self):
		gameId = 5428
		result = self.testObj.create(gameId)
		self.assertTrue(isinstance(result, model.GameModel))
		self.assertEqual(gameId, result.gameId)
