from src.lib import facebook
import logging

logging.getLogger().setLevel(logging.DEBUG)

class Facebook(object):
	instance = None
	@classmethod
	def getInstance(cls):
		if None != cls.instance:
			return cls.instance
		return Facebook()

	APP_ID = "247880815364832"
	APP_SECRET = "07b0648bd8f3c3318de53482a68126ee"	

	def __init__(self):
		self._graph = None

	def authenticateAsUser(self, requestDataAccessor):
		cookie = facebook.get_user_from_cookie(requestDataAccessor.getCookies(), Facebook.APP_ID, Facebook.APP_SECRET)
		self._graph = facebook.GraphAPI(cookie["access_token"])

	def getName(self, playerId):
		self._defaultAuthentication()
		profile = self._graph.get_object(playerId)
		if None == profile:
			return ""
		return profile["name"]

	def _defaultAuthentication(self):
		if None == self._graph:
			self._graph = facebook.GraphAPI()