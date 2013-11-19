#!/usr/bin/env python
import testhelper
import unittest
from mockito import *

import src.social

from src import social
from src import util
from src.lib import facebook

class UserTest(testhelper.TestCase):
	def setUp(self):
		self.playerId = "1234alkdjf"
		self.name = "Foobar Bingbaz, III"
		self._buildTestObj()

	def testGetNameReturnsExpectedName(self):
		self.assertEqual(self.name, self.testObj.getName())

	def testGetIdReturnsExpectedId(self):
		self.assertEqual(self.playerId, self.testObj.getId())

	def testUserHasExpectedDefaultValues(self):
		self.testObj = social.User.getInstance()
		self.assertEqual("", self.testObj.getName())
		self.assertEqual("", self.testObj.getId())

	def _buildTestObj(self):
		self.testObj = social.User.getInstance(self.playerId, self.name)

class FacebookTest(testhelper.TestCase):
	def setUp(self):
		self.requestDataAccessor = testhelper.createMock(util.RequestDataAccessor)
		self.graph = testhelper.createMock(facebook.GraphAPI)

		self.requestCookies = "pretty sweet cookies"
		self.fbCookie = {"access_token" : "23042098dlakj"}
		self.playerId = "234ojlksdj323"
		self.expectedName = "Foobar Bingbaz, Jr."
		self.expectedUser = testhelper.createMock(social.User)
		self.nullUser = testhelper.createMock(social.User)
		self.profile = {"name" : self.expectedName, "id" : self.playerId}

		self._doTraining()
		self._buildTestObj()

	def testAuthenticateAsUserGetsCorrectGraph(self):
		self.testObj.authenticateAsUser(self.requestDataAccessor)
		self.assertEqual(self.graph, self.testObj._graph)

	def testGetUserReturnsExpectedName(self):
		self.testObj.authenticateAsUser(self.requestDataAccessor)
		self.assertEqual(self.expectedUser, self.testObj.getUser(self.playerId))

	def testGetUserReturnsDefaultUserIfNoProfileFound(self):
		when(self.graph).get_object(self.playerId).thenReturn(None)
		self.testObj.authenticateAsUser(self.requestDataAccessor)
		self.assertEqual(self.nullUser, self.testObj.getUser(self.playerId))

	def testGetUserStillWorksNoAuthentication(self):
		self.assertEqual(self.expectedUser, self.testObj.getUser(self.playerId))

	def _doTraining(self):
		when(self.requestDataAccessor).getCookies().thenReturn(self.requestCookies)

		when(facebook).get_user_from_cookie(self.requestCookies, social.Facebook.APP_ID, social.Facebook.APP_SECRET).thenReturn(self.fbCookie)
		when(facebook).GraphAPI(self.fbCookie["access_token"]).thenReturn(self.graph)
		when(facebook).GraphAPI().thenReturn(self.graph)

		when(self.graph).get_object(self.playerId).thenReturn(self.profile)

		testhelper.replaceClass(src.social, "User", testhelper.createSimpleMock())
		when(src.social.User).getInstance(self.playerId, self.expectedName).thenReturn(self.expectedUser)
		when(src.social.User).getInstance().thenReturn(self.nullUser)

	def _buildTestObj(self):
		self.testObj = social.Facebook.getInstance()