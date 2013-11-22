import cgi
import webapp2
import jinja2
import os
import json
import logging
from google.appengine.ext import db
from google.appengine.ext import ndb
from google.appengine.api import users

import sys
sys.path.insert(1, './src')

import model
import game
import euchre
import serializer
import executable
import util
import web

jinjaEnvironment = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

config = {
	"webapp2_extras.sessions" : {
		"secret_key" : "A5BC5B49-A727-4080-BDCF-789D2E9586A3"
	}
}

class IndexPage(webapp2.RequestHandler):
	def post(self):
		self._handleRequest()

	def get(self):
		self._handleRequest()

	def _handleRequest(self):
		requestDataAccessor = util.RequestDataAccessor.getInstance(self.request)
		jsFileLoader = util.JsFileLoader.getInstance()
		pageDataBuilder = util.PageDataBuilder.getInstance(requestDataAccessor)
		templateValues = {
			"jsIncludes" : jsFileLoader.getJsHtml(),
			"pageData" : pageDataBuilder.buildData()
		}
		template = jinjaEnvironment.get_template('index.html')
		self.response.out.write(template.render(templateValues))

class AjaxHandler(web.SessionRequestHandler):
	def post(self):
		self.response.headers.add_header('content-type', 'application/json', charset='utf-8')
		executableFactory = executable.ExecutableFactory.getInstance(util.RequestDataAccessor.getInstance(self.request), util.ResponseWriter.getInstance(self.response), util.Session.getInstance(self.session))
		exe = executableFactory.createExecutable()
		exe.execute()

logging.getLogger().setLevel(logging.DEBUG)
app = webapp2.WSGIApplication([
	('/ajax', AjaxHandler),
	('/', IndexPage)
], debug=True, config=config)
