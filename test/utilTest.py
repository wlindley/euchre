#!/usr/bin/env python
from google.appengine.ext import ndb
import testhelper
from mockito import *

from src import util
from src import model

class RequestDataAccessorTest(testhelper.TestCase):
	def setUp(self):
		self.request = testhelper.createSimpleMock()
		self.testObj = util.RequestDataAccessor.getInstance(self.request)

	def testGetPassesThroughToRequest(self):
		params = "some key"
		expectedResult = "some data"
		when(self.request).get(params).thenReturn(expectedResult)
		result = self.testObj.get(params)
		self.assertEqual(expectedResult, result)

class ResponseWriterTest(testhelper.TestCase):
	def setUp(self):
		self.response = testhelper.createSimpleMock()
		self.testObj = util.ResponseWriter.getInstance(self.response)

	def testWritePassesThroughToResponse(self):
		params = "some response"
		self.testObj.write(params)
		verify(self.response).write(params)

class GameIdTrackerTest(testhelper.TestCase):
	def setUp(self):
		self.key = testhelper.createMock(ndb.Key)
		self.model = testhelper.createMock(model.GameIdModel)
		self.testObj = util.GameIdTracker.getInstance()
		self.testObj._getGameIdKey = lambda: self.key
		when(self.key).get().thenReturn(self.model)

	def testGetsAndIncrementsValue(self):
		expectedGameId = 100
		self.model.nextGameId = expectedGameId
		result = self.testObj.getGameId()
		self.assertEqual(expectedGameId, result)
		self.assertEqual(expectedGameId + 1, self.model.nextGameId)
		verify(self.model).put()

class JsFileLoaderTest(testhelper.TestCase):
	def setUp(self):
		self.filename = "jsFileList.txt"
		self.lines = ["js/foo.js\n", "js/bar.js\n"]
		self.fileReader = testhelper.createSingletonMock(util.FileReader)
		when(self.fileReader).getFileLines(self.filename).thenReturn(self.lines)
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
		when(mockFile).readlines().thenReturn(fileLines)
		self.testObj._getFile = lambda fname: mockFile if filename == fname else None
		result = self.testObj.getFileLines(filename)
		self.assertEqual(fileLines, result)
		verify(mockFile).close()
