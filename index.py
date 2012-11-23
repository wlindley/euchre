import cgi
import webapp2
import jinja2
import os
import json
from google.appengine.ext import db
from google.appengine.ext import ndb

import model
import game
import euchre
import serializer
import executable
import util

jinjaEnvironment = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

class IndexPage(webapp2.RequestHandler):
	def get(self):
		templateValues = {}
		template = jinjaEnvironment.get_template('index.html')
		self.response.out.write(template.render(templateValues))

class PlayerCreator(webapp2.RequestHandler):
	def get(self):
		self._handle()

	def post(self):
		self._handle()

	def _handle(self):
		playerId = self.request.get("playerId")
		player = model.PlayerModel(playerId=playerId)
		player.put()

		dbResults = db.GqlQuery("SELECT * FROM PlayerModel WHERE playerId IN :1", [playerId])

		result = {"numFound" : 0}
		for dbResult in dbResults:
			result["numFound"] += 1
			result["playerId"] = dbResult.playerId

		self.response.write(json.dumps(result))

class AjaxHandler(webapp2.RequestHandler):
	def post(self):
		executableFactory = executable.ExecutableFactory.getInstance(util.RequestDataAccessor.getInstance(self.request), util.ResponseWriter.getInstance(self.response))
		exe = executableFactory.createExecutable()
		exe.execute()

app = webapp2.WSGIApplication([
	('/createPlayer', PlayerCreator),
	('/createGame', GameCreator),
	('/', IndexPage)
], debug=True)
