from google.appengine.ext import ndb
import model
import json

class RequestDataAccessor(object):
	instance = None
	@classmethod
	def getInstance(cls, request):
		if None != cls.instance:
			return cls.instance
		return RequestDataAccessor(request)

	def __init__(self, request):
		self._request = request

	def get(self, key):
		return self._request.get(key)

	def getBaseUrl(self):
		return self._request.application_url

class ResponseWriter(object):
	instance = None
	@classmethod
	def getInstance(cls, response):
		if None != cls.instance:
			return cls.instance
		return ResponseWriter(response)

	def __init__(self, response):
		self._response = response

	def write(self, data):
		self._response.write(data)

class GameIdTracker(object):
	instance = None
	@classmethod
	def getInstance(cls):
		if None != cls.instance:
			return cls.instance
		return GameIdTracker()

	KEY_ID = "gameIdSingleton"

	def _getGameIdKey(self):
		return ndb.Key(model.GameIdModel, GameIdTracker.KEY_ID)

	def _getNewModel(self):
		return model.GameIdModel(nextGameId=0, id=GameIdTracker.KEY_ID)

	@ndb.transactional
	def getGameId(self):
		entity = self._getGameIdKey().get()
		if None == entity:
			entity = self._getNewModel()
		gameId = entity.nextGameId
		entity.nextGameId += 1
		entity.put()
		return gameId

class FileReader(object):
	instance = None
	@classmethod
	def getInstance(cls):
		if None != cls.instance:
			return cls.instance
		return FileReader()

	def getFileLines(self, filename):
		fileHandle = self._getFile(filename)
		if None == fileHandle:
			return []
		lines = fileHandle.readlines()
		fileHandle.close()
		return lines

	def _getFile(self, filename):
		try:
			fileHandle = open(filename)
			return fileHandle
		except IOError:
			pass
		return None

class JsFileLoader(object):
	instance = None
	@classmethod
	def getInstance(cls):
		if None != cls.instance:
			return cls.instance
		return JsFileLoader(FileReader.getInstance())

	JS_LIST_FILENAME = "jsFileList.txt"

	def __init__(self, fileReader):
		super(JsFileLoader, self).__init__()
		self._fileReader = fileReader

	def getJsHtml(self):
		lines = self._fileReader.getFileLines(JsFileLoader.JS_LIST_FILENAME)
		html = ""
		for line in lines:
			html += '\n<script src="%s" type="text/javascript"></script>' % (line.strip())
		return html

class PageDataBuilder(object):
	instance = None
	@classmethod
	def getInstance(cls, requestDataAccessor):
		if None != cls.instance:
			return cls.instance
		return PageDataBuilder(requestDataAccessor)

	AJAX_PATH = "/ajax"

	def __init__(self, requestDataAccessor):
		super(PageDataBuilder, self).__init__()
		self._requestDataAccessor = requestDataAccessor

	def buildData(self):
		pageData = {}
		pageData["playerId"] = self._requestDataAccessor.get("playerId")
		pageData["ajaxUrl"] = self._requestDataAccessor.getBaseUrl() + PageDataBuilder.AJAX_PATH
		return json.dumps(pageData)
