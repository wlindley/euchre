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
	def getInstance(cls, session):
		if None != cls.instance:
			return cls.instance
		return Facebook(session)

	APP_ID = "247880815364832"
	APP_SECRET = "07b0648bd8f3c3318de53482a68126ee"
	SESSION_KEY = "fbuser"

	def __init__(self, session):
		self._session = session
		self._graph = None

	def authenticateAsUser(self, requestDataAccessor):
		sessionData = self._session.get(Facebook.SESSION_KEY)
		if sessionData:
			accessToken = sessionData["accessToken"]
		else:
			cookie = facebook.get_user_from_cookie(requestDataAccessor.getCookies(), Facebook.APP_ID, Facebook.APP_SECRET)
			accessToken = cookie["access_token"]
			self._session.set(Facebook.SESSION_KEY, {"accessToken" : accessToken})
		self._graph = facebook.GraphAPI(accessToken)

	def getUser(self, identifier):
		self._defaultAuthentication()
		profile = self._graph.get_object(identifier)
		return self._buildUser(profile)

	def _defaultAuthentication(self):
		if None == self._graph:
			self._graph = facebook.GraphAPI()

	def _buildUser(self, fbProfile):
		if None == fbProfile:
			return User.getInstance()
		return User.getInstance(fbProfile["id"], fbProfile["name"])