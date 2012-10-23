from google.appengine.ext import db

class PlayerModel(db.Model):
	playerId = db.StringProperty(required=True)

class TurnTrackerModel(db.Model):
	pass
