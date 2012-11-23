#!/usr/bin/env python
from google.appengine.ext import ndb
import testhelper
import mock

from src import util
from src import model

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

class JsFileLoaderTest(testhelper.TestCase):
	def setUp(self):
		self.filename = "jsFileList.txt"
		self.lines = ["js/foo.js\n", "js/bar.js\n"]
		self.fileReader = testhelper.createSingletonMock(util.FileReader)
		self.fileReader.getFileLines.side_effect = lambda fname: self.lines if self.filename == fname else []
		self.testObj = util.JsFileLoader.getInstance()

	def testGetJsHtmlReturnsExpectedHtml(self):
		result = self.testObj.getJsHtml()
		self.assertEqual("""
<script src="js/foo.js" type="text/javascript"></script>
<script src="js/bar.js" type="text/javascript"></script>""", result)

class FileReaderTest(testhelper.TestCase):
	def setUp(self):
		self.testObj = util.FileReader.getInstance()

	def testGetFileLinesReturnsLinesOfFile(self):
		filename = "fooFile.dat"
		fileLines = ["one", "two", "three", "all of the lines"]
		mockFile = testhelper.createMock(file)
		mockFile.readlines.return_value = fileLines
		self.testObj._getFile = lambda fname: mockFile if filename == fname else None
		result = self.testObj.getFileLines(filename)
		self.assertEqual(fileLines, result)
		self.assertTrue(mockFile.close.called)
