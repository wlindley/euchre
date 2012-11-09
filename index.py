import cgi
import webapp2
import jinja2
import os
import json
from google.appengine.ext import db

import model

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

		pids = [playerId]
		dbResults = db.GqlQuery("SELECT * FROM PlayerModel WHERE playerId IN :1", pids)

		result = {"numFound" : 0}
		for dbResult in dbResults:
			result["numFound"] += 1
			result["playerId"] = dbResult.playerId

		self.response.write(json.dumps(result))

app = webapp2.WSGIApplication([
	('/createPlayer', PlayerCreator),
	('/', IndexPage)
], debug=True)
