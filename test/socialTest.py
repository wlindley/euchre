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
		self.session = testhelper.createSingletonMock(util.Session)
		self.graph = testhelper.createMock(facebook.GraphAPI)

		self.requestCookies = "pretty sweet cookies"
		self.accessToken = "23042098dlakj"
		self.fbCookie = {"access_token" : self.accessToken}
		self.playerId = "234ojlksdj323"
		self.expectedName = "Foobar Bingbaz, Jr."
		self.expectedUser = testhelper.createMock(social.User)
		self.nullUser = testhelper.createMock(social.User)
		self.profile = {"name" : self.expectedName, "id" : self.playerId}
		self.sessionData = {"accessToken" : self.accessToken}

		self._doTraining()
		self._buildTestObj()

	def testSuccessfulAuthenticateAsUserStoresDataInSession(self):
		self.testObj.authenticateAsUser(self.requestDataAccessor)
		verify(self.session).set(social.Facebook.SESSION_KEY, self.sessionData)

	def testGetUserReturnsExpectedName(self):
		self.testObj.authenticateAsUser(self.requestDataAccessor)
		self.assertEqual(self.expectedUser, self.testObj.getUser(self.playerId))

	def testGetUserReturnsDefaultUserIfNoProfileFound(self):
		when(self.graph).get_object(self.playerId).thenReturn(None)
		self.testObj.authenticateAsUser(self.requestDataAccessor)
		self.assertEqual(self.nullUser, self.testObj.getUser(self.playerId))

	def testGetUserStillWorksNoAuthentication(self):
		self.assertEqual(self.expectedUser, self.testObj.getUser(self.playerId))

	def testRetrievesDataFromSessionIfPresent(self):
		when(facebook).GraphAPI().thenReturn(None)
		when(self.session).get(social.Facebook.SESSION_KEY).thenReturn(self.sessionData)

		self.testObj.authenticateAsUser(self.requestDataAccessor)
		self.assertEqual(self.expectedUser, self.testObj.getUser(self.playerId))

		verify(facebook, never).get_user_from_cookie(any(), any(), any())

	def _doTraining(self):
		when(self.requestDataAccessor).getCookies().thenReturn(self.requestCookies)

		when(facebook).get_user_from_cookie(self.requestCookies, social.Facebook.APP_ID, social.Facebook.APP_SECRET).thenReturn(self.fbCookie)
		when(facebook).GraphAPI(self.accessToken).thenReturn(self.graph)
		when(facebook).GraphAPI().thenReturn(self.graph)

		when(self.graph).get_object(self.playerId).thenReturn(self.profile)

		testhelper.replaceClass(src.social, "User", testhelper.createSimpleMock())
		when(src.social.User).getInstance(self.playerId, self.expectedName).thenReturn(self.expectedUser)
		when(src.social.User).getInstance().thenReturn(self.nullUser)

	def _buildTestObj(self):
		self.testObj = social.Facebook.getInstance(self.session)