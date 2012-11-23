from google.appengine.ext import ndb
import model

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

	def _getGameIdKey(self):
		return ndb.Key(model.GameIdModel, "gameIdSingleton")

	@ndb.transactional
	def getGameId(self):
		entity = self._getGameIdKey().get()
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
