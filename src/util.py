from google.appengine.ext import ndb
from google.appengine.api import app_identity
import model
import json
import os.path
import glob

from src import euchre
import social

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

	def getCookies(self):
		return self._request.cookies

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

class Session(object):
	instance = None
	@classmethod
	def getInstance(cls, sessionStore):
		if None != cls.instance:
			return cls.instance
		return Session(sessionStore)

	def __init__(self, sessionStore):
		self._sessionStore = sessionStore

	def get(self, key):
		return self._sessionStore.get(key)

	def set(self, key, value):
		self._sessionStore[key] = value

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

	def getFileContents(self, filename):
		fileHandle = self._getFile(filename)
		if None == fileHandle:
			return ""
		contents = fileHandle.read()
		fileHandle.close()
		return contents

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

	JS_LIST_FILENAME = "data/jsFileList.txt"

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
		return PageDataBuilder(requestDataAccessor, TemplateManager.getInstance(), FileReader.getInstance())

	AJAX_PATH = "/ajax"
	CHANNEL_PATH = "/data/channel.html"
	TEMPLATE_PATTERN  = "templates/*.template"

	def __init__(self, requestDataAccessor, templateManager, fileReader):
		super(PageDataBuilder, self).__init__()
		self._requestDataAccessor = requestDataAccessor
		self._templateManager = templateManager
		self._fileReader = fileReader

	def buildData(self):
		pageData = {}
		pageData["appId"] = social.Facebook.APP_ID
		pageData["ajaxUrl"] = self._requestDataAccessor.getBaseUrl() + PageDataBuilder.AJAX_PATH
		pageData["channelUrl"] = self._requestDataAccessor.getBaseUrl() + PageDataBuilder.CHANNEL_PATH
		self._templateManager.loadTemplates(glob.glob(PageDataBuilder.TEMPLATE_PATTERN))
		pageData["templates"] = self._templateManager.getTemplates()
		pageData["locStrings"] = json.loads(self._fileReader.getFileContents("data/locStrings.json"))
		return json.dumps(pageData)

class TemplateManager(object):
	instance = None
	@classmethod
	def getInstance(cls):
		if None != cls.instance:
			return cls.instance
		return TemplateManager(FileReader.getInstance())

	def __init__(self, fileReader):
		super(TemplateManager, self).__init__()
		self._fileReader = fileReader
		self._templates = {}

	def loadTemplates(self, filenames):
		for filename in filenames:
			templateId = os.path.basename(filename).replace(".template", "")
			self._templates[templateId] = self._fileReader.getFileContents(filename)

	def getTemplates(self):
		return self._templates

class ConfigManager(object):
	instance = None
	@classmethod
	def getInstance(cls):
		if None != cls.instance:
			return cls.instance
		return ConfigManager(FileReader.getInstance())

	def __init__(self, fileReader):
		self._fileReader = fileReader
		self._data = {}

	def loadFromDir(self, rootDir):
		self._loadDataFile(os.path.join(rootDir, "common.config"))
		self._loadDataFile(os.path.join(rootDir, self._getEnvironmentFilename()))

	def get(self, key, default=None):
		if not key in self._data:
			return default
		return self._data[key]

	def _getEnvironmentFilename(self):
		appId = app_identity.get_application_id()
		if "familyeuchre-staging" == appId:
			return "staging.config"
		elif "familyeuchre-local" == appId:
			return "local.config"
		return "production.config"

	def _loadDataFile(self, filename):
		data = json.loads(self._fileReader.getFileContents(filename))
		for key,value in data.iteritems():
			self._data[key] = value