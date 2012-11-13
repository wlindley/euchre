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

class GameCreator(webapp2.RequestHandler):
	def get(self):
		self._handle()

	def post(self):
		self._handle()

	def _handle(self):
		gameId = int(self.request.get("gameId"))
		playerIds = self.request.get("players").split(",")
		players = [game.Player.getInstance(pid) for pid in playerIds]
		team1 = self.request.get("team1").split(",")
		team2 = self.request.get("team2").split(",")
		teams = {0 : team1, 1 : team2}
		gameObj = euchre.Game.getInstance(players, teams)
		gameObj.startGame()
		serializedGame = json.dumps(serializer.GameSerializer.getInstance().serialize(gameObj))

		gameModel = model.GameModel(gameId=gameId, serializedGame=serializedGame, playerId=playerIds)
		gameModel.put()

		#dbResults = ndb.GqlQuery("SELECT * FROM GameModel WHERE gameId in :1", [gameId])
		query = model.GameModel.query(model.GameModel.gameId == gameId)
		dbResults = query.fetch(1)
		result = {"numFound" : 0}
		for dbResult in dbResults:
			result["numFound"] += 1
			result["game"] = dbResult.serializedGame

		self.response.write(json.dumps(result))

app = webapp2.WSGIApplication([
	('/createPlayer', PlayerCreator),
	('/createGame', GameCreator),
	('/', IndexPage)
], debug=True)
