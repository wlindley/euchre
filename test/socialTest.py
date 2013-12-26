#!/usr/bin/env python
import testhelper
import unittest
from mockito import *
import urllib2

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
		self.configManager = testhelper.createSingletonMock(util.ConfigManager)

		self.requestCookies = "pretty sweet cookies"
		self.accessToken = "23042098dlakj"
		self.fbCookie = {"access_token" : self.accessToken}
		self.playerId = "234ojlksdj323"
		self.expectedName = "Foobar Bingbaz, Jr."
		self.expectedUser = testhelper.createMock(social.User)
		self.nullUser = testhelper.createMock(social.User)
		self.profile = {"name" : self.expectedName, "id" : self.playerId}
		self.sessionData = {"accessToken" : self.accessToken}
		self.sessionKey = "fbuser"
		self.appId = "4873248102985"
		self.appSecret = "23049804w9rasdlfaj234094239lskdjds"

		self._doTraining()
		self._buildTestObj()

	def testGetUserReturnsExpectedName(self):
		self.assertEqual(self.expectedUser, self.testObj.getUser(self.playerId))

	def testGetUserReturnsDefaultUserIfNoProfileFound(self):
		when(self.graph).get_object(self.playerId).thenReturn(None)
		self.assertEqual(self.nullUser, self.testObj.getUser(self.playerId))

	def testSuccessfulAuthenticateAsUserStoresDataInSession(self):
		self.testObj.getUser(self.playerId)
		verify(self.session).set(self.sessionKey, self.sessionData)

	def testGetUserStillWorksNoAuthentication(self):
		when(facebook).get_user_from_cookie(any(), any(), any()).thenReturn(None)
		when(facebook).GraphAPI().thenReturn(self.graph)
		self.assertEqual(self.expectedUser, self.testObj.getUser(self.playerId))

	def testGetUserStillWorksWhenAuthenticationRaisesException(self):
		when(facebook).get_user_from_cookie(any(), any(), any()).thenRaise(urllib2.HTTPError(400, "testing", None, None, None))
		when(facebook).GraphAPI().thenReturn(self.graph)
		self.assertEqual(self.expectedUser, self.testObj.getUser(self.playerId))

	def testRetrievesDataFromSessionIfPresent(self):
		when(self.session).get(self.sessionKey).thenReturn(self.sessionData)

		self.assertEqual(self.expectedUser, self.testObj.getUser(self.playerId))

		verify(facebook, never).get_user_from_cookie(any(), any(), any())

	def testClearsSessionIfGetObjectRaisesGraphAPIErrorAndTriesAgain(self):
		when(self.graph).get_object(self.playerId).thenRaise(facebook.GraphAPIError({"type" : "bar"})).thenReturn(self.profile)

		self.assertEqual(self.expectedUser, self.testObj.getUser(self.playerId))

		verify(self.session).set(self.sessionKey, None)

	def testReturnsDefaultUserIfRetryFails(self):
		when(self.graph).get_object(self.playerId).thenRaise(facebook.GraphAPIError({"type" : "bar"}))

		self.assertEqual(self.nullUser, self.testObj.getUser(self.playerId))

	def _doTraining(self):
		when(self.requestDataAccessor).getCookies().thenReturn(self.requestCookies)

		when(facebook).get_user_from_cookie(self.requestCookies, self.appId, self.appSecret).thenReturn(self.fbCookie)
		when(facebook).GraphAPI(self.accessToken).thenReturn(self.graph)

		when(self.graph).get_object(self.playerId).thenReturn(self.profile)

		testhelper.replaceClass(src.social, "User", testhelper.createSimpleMock())
		when(src.social.User).getInstance(self.playerId, self.expectedName).thenReturn(self.expectedUser)
		when(src.social.User).getInstance().thenReturn(self.nullUser)

		when(self.configManager).get("FB.sessionKey").thenReturn(self.sessionKey)
		when(self.configManager).get("FB.appId").thenReturn(self.appId)
		when(self.configManager).get("FB.appSecret").thenReturn(self.appSecret)

	def _buildTestObj(self):
		self.testObj = social.Facebook.getInstance(self.requestDataAccessor, self.session)