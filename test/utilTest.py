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

	def testGetCreatesModelIfItDoesNotExist(self):
		when(self.key).get().thenReturn(None)
		self.model.nextGameId = 0
		self.testObj._getNewModel = lambda: self.model
		self.assertEqual(0, self.testObj.getGameId())
		self.assertEqual(1, self.testObj.getGameId())

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
		self.expectedData = {
			"ajaxUrl" : self.baseUrl + "/ajax",
			"playerId" : self.playerId,
			"templates" : self.templates
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

class HandRetrieverTest(testhelper.TestCase):
	def setUp(self):
		self.players = [game.Player("1"), game.Player("2"), game.Player("3"), game.Player("4")]
		self.teams = [["1", "2"], ["3", "4"]]
		self.game = euchre.Game.getInstance(self.players, self.teams)
		self.testObj = util.HandRetriever.getInstance()

	def testGetHandReturnsCorrectData(self):
		playerId = "2"
		self.game.startGame()
		expectedHand = self.game._curSequence._round.hands[playerId]
		result = self.testObj.getHand(playerId, self.game)
		self.assertEqual(expectedHand, result)

	def testGetHandReturnsEmptyListWhenGameNotStarted(self):
		playerId = "1"
		result = self.testObj.getHand(playerId, self.game)
		self.assertEqual([], result)

	def testGetHandReturnsEmptyListWhenPlayerIdNotInGame(self):
		playerId = "8"
		self.game.startGame()
		result = self.testObj.getHand(playerId, self.game)
		self.assertEqual([], result)

class TurnRetrieverTest(testhelper.TestCase):
	def setUp(self):
		self.players = [game.Player("1"), game.Player("2"), game.Player("3"), game.Player("4")]
		self.teams = [["1", "2"], ["3", "4"]]
		self.sequence = testhelper.createSingletonMock(euchre.Sequence)
		self.trumpTurnTracker = testhelper.createMock(game.TurnTracker)
		self.roundTurnTracker = testhelper.createMock(game.TurnTracker)
		self.round = testhelper.createSingletonMock(euchre.Round)
		self.trumpSelector = testhelper.createSingletonMock(euchre.TrumpSelector)
		when(self.sequence).getRound().thenReturn(self.round)
		when(self.sequence).getTrumpSelector().thenReturn(self.trumpSelector)
		when(self.round).getTurnTracker().thenReturn(self.roundTurnTracker)
		when(self.trumpSelector).getTurnTracker().thenReturn(self.trumpTurnTracker)
		self.game = euchre.Game.getInstance(self.players, self.teams)
		self.testObj = util.TurnRetriever.getInstance()

	def testReturnsCorrectDataDuringTrumpSelection(self):
		currentPlayer = "3"
		when(self.trumpTurnTracker).getCurrentPlayerId().thenReturn(currentPlayer)
		when(self.sequence).getState().thenReturn(euchre.Sequence.STATE_TRUMP_SELECTION)
		self.game.startGame()
		result = self.testObj.retrieveTurn(self.game)
		self.assertEqual(currentPlayer, result)

	def testReturnsCorrectDataDuringTrumpSelection2(self):
		currentPlayer = "2"
		when(self.trumpTurnTracker).getCurrentPlayerId().thenReturn(currentPlayer)
		when(self.sequence).getState().thenReturn(euchre.Sequence.STATE_TRUMP_SELECTION_2)
		self.game.startGame()
		result = self.testObj.retrieveTurn(self.game)
		self.assertEqual(currentPlayer, result)

	def testReturnsCorrectDataDuringGamePlay(self):
		currentPlayer = "4"
		when(self.roundTurnTracker).getCurrentPlayerId().thenReturn(currentPlayer)
		when(self.sequence).getState().thenReturn(euchre.Sequence.STATE_PLAYING_ROUND)
		self.game.startGame()
		result = self.testObj.retrieveTurn(self.game)
		self.assertEqual(currentPlayer, result)

	def testReturnsNoneIfGameNotStarted(self):
		result = self.testObj.retrieveTurn(self.game)
		self.assertEqual(None, result)

	def testReturnsNoneIfSequenceIsInAnotherState(self):
		self.game.startGame()
		when(self.roundTurnTracker).getCurrentPlayerId().thenReturn("1")
		when(self.trumpTurnTracker).getCurrentPlayerId().thenReturn("2")
		when(self.sequence).getState().thenReturn(euchre.Sequence.STATE_INVALID)
		result = self.testObj.retrieveTurn(self.game)
		self.assertEqual(None, result)
