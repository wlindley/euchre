#!/usr/bin/env python
from google.appengine.ext import ndb
import testhelper
import json
import os.path
import glob
from mockito import *

import google.appengine.api.app_identity

from src import util
from src import model
from src import game
from src import euchre
from src import social

class RequestDataAccessorTest(testhelper.TestCase):
	def setUp(self):
		self.applicationUrl = "http://sweetapp.com"
		self.key = "some key"
		self.expectedResult = "some data"
		self.cookies = ["123", "sdlkj", "324jd"]

		self.request = testhelper.createSimpleMock()
		self.request.application_url = self.applicationUrl
		self.request.cookies = self.cookies

		when(self.request).get(self.key).thenReturn(self.expectedResult)
		self.testObj = util.RequestDataAccessor.getInstance(self.request)

	def testGetPassesThroughToRequest(self):
		result = self.testObj.get(self.key)
		self.assertEqual(self.expectedResult, result)

	def testGetBaseUrlReturnsApplicationUrl(self):
		self.assertEqual(self.applicationUrl, self.testObj.getBaseUrl())

	def testGetCookiesReturnsCookies(self):
		self.assertEqual(self.cookies, self.testObj.getCookies())

class ResponseWriterTest(testhelper.TestCase):
	def setUp(self):
		self.response = testhelper.createSimpleMock()
		self.testObj = util.ResponseWriter.getInstance(self.response)

	def testWritePassesThroughToResponse(self):
		params = "some response"
		self.testObj.write(params)
		verify(self.response).write(params)

class SessionTest(testhelper.TestCase):
	def setUp(self):
		self.sessionStore = testhelper.createSimpleMock()

		self.key = "foouser"
		self.expectedValue = {"userid" : "2309asdlj3"}

		when(self.sessionStore).get(self.key).thenReturn(self.expectedValue)

		self._buildTestObj()

	def _buildTestObj(self):
		self.testObj = util.Session.getInstance(self.sessionStore)

	def testGetReturnsExpectedValue(self):
		self.assertEqual(self.expectedValue, self.testObj.get(self.key))

	def testSetUpdatesValue(self):
		updatedValue = {"userid" : "bing"}
		self.sessionStore = {self.key : self.expectedValue}
		self._buildTestObj()

		self.testObj.set(self.key, updatedValue)

		self.assertEqual(updatedValue, self.sessionStore[self.key])

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
		mockFile = testhelper.createSimpleMock() #file object
		when(mockFile).readlines().thenReturn(fileLines)
		self.testObj._getFile = lambda fname: mockFile if filename == fname else None
		result = self.testObj.getFileLines(filename)
		self.assertEqual(fileLines, result)
		verify(mockFile).close()

	def testGetFileContentsReturnsContentsOfFile(self):
		filename = "bar_file.info"
		fileContents = "the best file ever\nis not at this location"
		mockFile = testhelper.createSimpleMock() #file object
		when(mockFile).read().thenReturn(fileContents)
		self.testObj._getFile = lambda fname: mockFile if filename == fname else None
		result = self.testObj.getFileContents(filename)
		self.assertEqual(fileContents, result)
		verify(mockFile).close()

class PageDataBuilderTest(testhelper.TestCase):
	def setUp(self):
		self.baseUrl = "http://awesomest.url.ever"
		self.templateFiles = "some filenames"
		self.templates = "the best templates ever"
		self.locStrings = {"foo" : "all of the localized strings"}
		self.appId = "23049279483"
		self.environment = "foo_env"
		self.expectedData = {
			"ajaxUrl" : self.baseUrl + "/ajax",
			"templates" : self.templates,
			"locStrings" : self.locStrings,
			"appId" : self.appId,
			"environment" : self.environment,
			"channelUrl" : self.baseUrl + "/data/channel.html"
		}
		self.expectedTemplates = None

		self.requestDataAccessor = testhelper.createSingletonMock(util.RequestDataAccessor)
		when(self.requestDataAccessor).getBaseUrl().thenReturn(self.baseUrl)
		when(util.glob).glob("templates/*.template").thenReturn(self.templateFiles)
		self.templateManager = testhelper.createSingletonMock(util.TemplateManager)
		def replaceLoadTemplates(filenames):
			if self.templateFiles == filenames:
				self.expectedTemplates = self.templates
		self.templateManager.loadTemplates = replaceLoadTemplates
		self.templateManager.getTemplates = lambda: self.expectedTemplates

		self.fileLoader = testhelper.createSingletonMock(util.FileReader)
		when(self.fileLoader).getFileContents("data/locStrings.json").thenReturn(json.dumps(self.locStrings))

		self.configManager = testhelper.createSingletonMock(util.ConfigManager)
		when(self.configManager).get("FB.appId").thenReturn(self.appId)
		when(self.configManager).get("environment").thenReturn(self.environment)

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

class ConfigManagerTest(testhelper.TestCase):
	def setUp(self):
		self.fileReader = testhelper.createSingletonMock(util.FileReader)

		self.rootDir = "data/config"

		self.baseFilename = "common.config"
		self.baseFileContents = '{"foo" : 1, "bar" : 2}'
		self.prodFilename = "production.config"
		self.prodFileContents = '{"environment" : "production"}'
		self.stageFilename = "staging.config"
		self.stageFileContents = '{"environment" : "staging"}'
		self.localFilename = "local.config"
		self.localFileContents = '{"environment" : "local"}'

		when(self.fileReader).getFileContents(self.rootDir + "/" + self.baseFilename).thenReturn(self.baseFileContents)
		when(self.fileReader).getFileContents(self.rootDir + "/" + self.prodFilename).thenReturn(self.prodFileContents)
		when(self.fileReader).getFileContents(self.rootDir + "/" + self.stageFilename).thenReturn(self.stageFileContents)
		when(self.fileReader).getFileContents(self.rootDir + "/" + self.localFilename).thenReturn(self.localFileContents)

		self._buildTestObj()

	def _buildTestObj(self):
		self.testObj = util.ConfigManager.getInstance()

	def _trainAppId(self, appId):
		when(google.appengine.api.app_identity).get_application_id().thenReturn(appId)

	def _verifyConfig(self, expectedEnvironment):
		self.assertEqual(1, self.testObj.get("foo"))
		self.assertEqual(2, self.testObj.get("bar"))
		self.assertEqual(expectedEnvironment, self.testObj.get("environment"))

	def testLoadsConfigCorrectsForProduction(self):
		self._trainAppId("familyeuchre")
		self._buildTestObj()
		self._verifyConfig("production")

	def testLoadsConfigCorrectsForStaging(self):
		self._trainAppId("familyeuchre-staging")
		self._buildTestObj()
		self._verifyConfig("staging")

	def testLoadsConfigCorrectsForLocal(self):
		self._trainAppId("familyeuchre-local")
		self._buildTestObj()
		self._verifyConfig("local")

	def testReturnsDefaultValueIfKeyIsNotPresent(self):
		self._trainAppId("familyeuchre")
		self._buildTestObj()
		self.assertEqual("hello", self.testObj.get("greeting", "hello"))

	def testReturnsNoneIfKeyIsNotPresentAndNoDefaultSpecified(self):
		self._trainAppId("familyeuchre")
		self._buildTestObj()
		self.assertEqual(None, self.testObj.get("greeting"))