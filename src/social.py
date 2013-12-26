from src.lib import facebook
import logging

import util

logging.getLogger().setLevel(logging.DEBUG)

class User(object):
	instance = None
	@classmethod
	def getInstance(cls, playerId="", name=""):
		if None != cls.instance:
			return cls.instance
		return User(playerId, name)

	def __init__(self, playerId="", name=""):
		self._playerId = playerId
		self._name = name

	def getName(self):
		return self._name

	def getId(self):
		return self._playerId

class Facebook(object):
	instance = None
	@classmethod
	def getInstance(cls, requestDataAccessor, session):
		if None != cls.instance:
			return cls.instance
		return Facebook(requestDataAccessor, session, util.ConfigManager.getInstance())

	def __init__(self, requestDataAccessor, session, configManager):
		self._requestDataAccessor = requestDataAccessor
		self._session = session
		self._configManager = configManager
		self._graph = None

	def getUser(self, identifier):
		self._defaultAuthentication()
		try:
			profile = self._graph.get_object(identifier)
		except facebook.GraphAPIError as e:
			#may just want to do this for error codes 190 and 191
			logging.info("Facebook Graph error while getting user, error type: %s" % e.result)
			self._session.set(self._configManager.get("FB.sessionKey"), None)
			self._graph = None
			self._defaultAuthentication()
			try:
				profile = self._graph.get_object(identifier)
			except facebook.GraphAPIError as e:
				logging.info("Facebook Graph error while retrying user get, error type: %s" % e.result)
				profile = None

		return self._buildUser(profile)

	def _defaultAuthentication(self):
		if None != self._graph:
			return

		#first, try session
		sessionData = self._session.get(self._configManager.get("FB.sessionKey"))
		if sessionData:
			logging.info("Facebook access token found in session data")
			accessToken = sessionData["accessToken"]
		else:
			#second, try cookies
			try:
				cookie = facebook.get_user_from_cookie(self._requestDataAccessor.getCookies(), self._configManager.get("FB.appId"), self._configManager.get("FB.appSecret"))
			except Exception as e:
				logging.error("Error while trying to retrieve Facebook cookie: %s" % e)
				cookie = None
			if None == cookie:
				#give up and use default
				logging.info("Facebook access token could not be obtained, using unauthenticated GraphAPI object")
				self._graph = facebook.GraphAPI()
				return
			logging.info("Facebbok access token retrieved from cookies")
			accessToken = cookie["access_token"]
			self._session.set(self._configManager.get("FB.sessionKey"), {"accessToken" : accessToken})
		self._graph = facebook.GraphAPI(accessToken)

	def _buildUser(self, fbProfile):
		if None == fbProfile:
			return User.getInstance()
		return User.getInstance(fbProfile["id"], fbProfile["name"])