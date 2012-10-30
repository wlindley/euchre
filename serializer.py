from abc import ABCMeta
from abc import abstractmethod
import game
import euchre

class AbstractSerializer(object):
	__metaclass__ = ABCMeta

	@abstractmethod
	def canSerialize(self, obj):
		return False

	@abstractmethod
	def serialize(self, obj):
		return {}

	@abstractmethod
	def deserialize(self, data):
		return None

class PlayerSerializer(AbstractSerializer):
	instance = None
	@classmethod
	def getInstance(cls):
		if None != cls.instance:
			return cls.instance
		return PlayerSerializer()

	def canSerialize(self, obj):
		return isinstance(obj, game.Player)

	def serialize(self, obj):
		return {"playerId" : obj.playerId}

	def deserialize(self, data):
		return game.Player(data["playerId"])

class GameSerializer(AbstractSerializer):
	instance = None
	@classmethod
	def getInstance(cls):
		if None != cls.instance:
			return cls.instance
		return GameSerializer(PlayerSerializer.getInstance(), ScoreTrackerSerializer.getInstance(), SequenceSerializer.getInstance())

	def __init__(self, playerSerializer, scoreTrackerSerializer, sequenceSerializer):
		self.playerSerializer = playerSerializer
		self.scoreTrackerSerializer = scoreTrackerSerializer
		self.sequenceSerializer = sequenceSerializer

	def canSerialize(self, obj):
		return isinstance(obj, euchre.Game)

	def serialize(self, obj):
		return {"players" : self._serializePlayers(obj._players),
				"scoreTracker" : self.scoreTrackerSerializer.serialize(obj._scoreTracker),
				"curSequence" : self.sequenceSerializer.serialize(obj._curSequence)}

	def _serializePlayers(self, players):
		serializedPlayers = []
		for player in players:
			serializedPlayers.append(self.playerSerializer.serialize(player))
		return serializedPlayers

	def deserialize(self, data):
		players = self._deserializePlayers(data["players"])
		scoreTracker = self.scoreTrackerSerializer.deserialize(data["scoreTracker"])
		game = euchre.Game(players, scoreTracker, euchre.SequenceFactory.getInstance())
		game._curSequence = self.sequenceSerializer.deserialize(data["curSequence"])
		return game

	def _deserializePlayers(self, playersData):
		players = []
		for data in playersData:
			players.append(self.playerSerializer.deserialize(data))
		return players

class ScoreTrackerSerializer(AbstractSerializer):
	instance = None
	@classmethod
	def getInstance(cls):
		if None != cls.instance:
			return cls.instance
		return ScoreTrackerSerializer()

class SequenceSerializer(AbstractSerializer):
	instance = None
	@classmethod
	def getInstance(cls):
		if None != cls.instance:
			return cls.instance
		return SequenceSerializer()
