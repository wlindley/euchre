from src.lib import facebook
import logging

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
		return Facebook(requestDataAccessor, session)

	APP_ID = "247880815364832"
	APP_SECRET = "07b0648bd8f3c3318de53482a68126ee"
	SESSION_KEY = "fbuser"

	def __init__(self, requestDataAccessor, session):
		self._requestDataAccessor = requestDataAccessor
		self._session = session
		self._graph = None

	def getUser(self, identifier):
		self._defaultAuthentication()
		try:
			profile = self._graph.get_object(identifier)
		except facebook.GraphAPIError as e:
			#may just want to do this for error codes 190 and 191
			logging.info("Facebook Graph error while getting user, error type: %s" % e.result)
			self._session.set(Facebook.SESSION_KEY, None)
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
		sessionData = self._session.get(Facebook.SESSION_KEY)
		if sessionData:
			logging.info("Facebook access token found in session data")
			accessToken = sessionData["accessToken"]
		else:
			#second, try cookies
			cookie = facebook.get_user_from_cookie(self._requestDataAccessor.getCookies(), Facebook.APP_ID, Facebook.APP_SECRET)
			if None == cookie:
				#give up and use default
				logging.info("Facebook access token could not be obtained, using unauthenticated GraphAPI object")
				self._graph = facebook.GraphAPI()
				return
			logging.info("Facebbok access token retrieved from cookies")
			accessToken = cookie["access_token"]
			self._session.set(Facebook.SESSION_KEY, {"accessToken" : accessToken})
		self._graph = facebook.GraphAPI(accessToken)

	def _buildUser(self, fbProfile):
		if None == fbProfile:
			return User.getInstance()
		return User.getInstance(fbProfile["id"], fbProfile["name"])