#!/usr/bin/env python
from google.appengine.ext import ndb
import testhelper
import json
import os.path
import glob
from mockito import *

from src import util
from src import model
from src import game
from src import euchre

class RequestDataAccessorTest(testhelper.TestCase):
	def setUp(self):
		self.applicationUrl = "http://sweetapp.com"
		self.key = "some key"
		self.expectedResult = "some data"
		self.request = testhelper.createSimpleMock()
		self.request.application_url = self.applicationUrl
		when(self.request).get(self.key).thenReturn(self.expectedResult)
		self.testObj = util.RequestDataAccessor.getInstance(self.request)

	def testGetPassesThroughToRequest(self):
		result = self.testObj.get(self.key)
		self.assertEqual(self.expectedResult, result)

	def testGetBaseUrlReturnsApplicationUrl(self):
		self.assertEqual(self.applicationUrl, self.testObj.getBaseUrl())

class ResponseWriterTest(testhelper.TestCase):
	def setUp(self):
		self.response = testhelper.createSimpleMock()
		self.testObj = util.ResponseWriter.getInstance(self.response)

	def testWritePassesThroughToResponse(self):
		params = "some response"
		self.testObj.write(params)
		verify(self.response).write(params)

class JsFileLoaderTest(testhelper.TestCase):
	def setUp(self):
		self.filename = "data/jsFileList.txt"
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

	def testGetFileContentsReturnsContentsOfFile(self):
		filename = "bar_file.info"
		fileContents = "the best file ever\nis not at this location"
		mockFile = testhelper.createMock(file)
		when(mockFile).read().thenReturn(fileContents)
		self.testObj._getFile = lambda fname: mockFile if filename == fname else None
		result = self.testObj.getFileContents(filename)
		self.assertEqual(fileContents, result)
		verify(mockFile).close()

class PageDataBuilderTest(testhelper.TestCase):
	def setUp(self):
		self.baseUrl = "http://awesomest.url.ever"
		self.playerId = "123456"
		self.templateFiles = "some filenames"
		self.templates = "the best templates ever"
		self.locStrings = {"foo" : "all of the localized strings"}
		self.expectedData = {
			"ajaxUrl" : self.baseUrl + "/ajax",
			"playerId" : self.playerId,
			"templates" : self.templates,
			"locStrings" : self.locStrings
		}
		self.expectedTemplates = None

		self.requestDataAccessor = testhelper.createSingletonMock(util.RequestDataAccessor)
		when(self.requestDataAccessor).getBaseUrl().thenReturn(self.baseUrl)
		when(self.requestDataAccessor).get("playerId").thenReturn(self.playerId)
		when(util.glob).glob("templates/*.template").thenReturn(self.templateFiles)
		self.templateManager = testhelper.createSingletonMock(util.TemplateManager)
		def replaceLoadTemplates(filenames):
			if self.templateFiles == filenames:
				self.expectedTemplates = self.templates
		self.templateManager.loadTemplates = replaceLoadTemplates
		self.templateManager.getTemplates = lambda: self.expectedTemplates

		self.fileLoader = testhelper.createSingletonMock(util.FileReader)
		when(self.fileLoader).getFileContents("data/locStrings.json").thenReturn(json.dumps(self.locStrings))

		self.testObj = util.PageDataBuilder.getInstance(self.requestDataAccessor)

	def testBuildDataIncludesExpectedKeys(self):
		result = json.loads(self.testObj.buildData())
		for key, value in self.expectedData.iteritems():
			self.assertIn(key, result)
			self.assertEqual(value, result[key])

class TemplateManagerTest(testhelper.TestCase):
	def setUp(self):
		self.filenames = ["temp/foo.template", "bar.template", "bin/div.template"]
		self.contents = [["<html></html>"], ["<h1>sweeeeeet text</h1>"], ["<div class=\"foobar\"></div>"]]
		self.fileReader = testhelper.createSingletonMock(util.FileReader)
		for i in range(len(self.filenames)):
			when(self.fileReader).getFileContents(self.filenames[i]).thenReturn(self.contents[i])
		self.testObj = util.TemplateManager.getInstance()

	def testGetTemplatesReturnsLoadedTemplates(self):
		self.testObj.loadTemplates(self.filenames)
		result = self.testObj.getTemplates()
		for i in range(len(self.filenames)):
			templateId = os.path.basename(self.filenames[i]).replace(".template", "")
			self.assertIn(templateId, result)
			self.assertEqual(self.contents[i], result[templateId])
