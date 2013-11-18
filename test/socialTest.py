#!/usr/bin/env python
import testhelper
import unittest
from mockito import *

from src import social
from src import util
from src.lib import facebook

class FacebookTest(testhelper.TestCase):
	def setUp(self):
		self.requestDataAccessor = testhelper.createMock(util.RequestDataAccessor)
		self.graph = testhelper.createMock(facebook.GraphAPI)

		self.requestCookies = "pretty sweet cookies"
		self.fbCookie = {"access_token" : "23042098dlakj"}
		self.playerId = "234ojlksdj323"
		self.expectedName = "Foobar Bingbaz, Jr."
		self.profile = {"name" : self.expectedName}

		self._doTraining()
		self._buildTestObj()

	def testAuthenticateAsUserGetsCorrectGraph(self):
		self.testObj.authenticateAsUser(self.requestDataAccessor)
		self.assertEqual(self.graph, self.testObj._graph)

	def testGetNameReturnsExpectedName(self):
		self.testObj.authenticateAsUser(self.requestDataAccessor)
		self.assertEqual(self.expectedName, self.testObj.getName(self.playerId))

	def testGetNameReturnsEmptyStringIfNoProfileFound(self):
		when(self.graph).get_object(self.playerId).thenReturn(None)
		self.testObj.authenticateAsUser(self.requestDataAccessor)
		self.assertEqual("", self.testObj.getName(self.playerId))

	def testGetNameStillWorksNoAuthentication(self):
		self.assertEqual(self.expectedName, self.testObj.getName(self.playerId))

	def _doTraining(self):
		when(self.requestDataAccessor).getCookies().thenReturn(self.requestCookies)
		when(facebook).get_user_from_cookie(self.requestCookies, social.Facebook.APP_ID, social.Facebook.APP_SECRET).thenReturn(self.fbCookie)
		when(facebook).GraphAPI(self.fbCookie["access_token"]).thenReturn(self.graph)
		when(facebook).GraphAPI().thenReturn(self.graph)
		when(self.graph).get_object(self.playerId).thenReturn(self.profile)

	def _buildTestObj(self):
		self.testObj = social.Facebook.getInstance()