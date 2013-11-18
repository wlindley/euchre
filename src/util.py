from google.appengine.ext import ndb
import model
import json
import os.path
import glob

from src import euchre

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
	TEMPLATE_PATTERN  = "templates/*.template"

	def __init__(self, requestDataAccessor, templateManager, fileReader):
		super(PageDataBuilder, self).__init__()
		self._requestDataAccessor = requestDataAccessor
		self._templateManager = templateManager
		self._fileReader = fileReader

	def buildData(self):
		pageData = {}
		pageData["playerId"] = self._requestDataAccessor.get("playerId")
		pageData["ajaxUrl"] = self._requestDataAccessor.getBaseUrl() + PageDataBuilder.AJAX_PATH
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
