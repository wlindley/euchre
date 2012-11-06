from google.appengine.ext import db

class PlayerModel(db.Model):
	playerId = db.StringProperty(required=True)

class GameModle(db.Model):
	gameId = db.StringProperty(required=True)
	serializedGame = db.TextProperty()
