from abc import ABCMeta
from abc import abstractmethod
import game
import euchre

class AbstractSerializer(object):
	__metaclass__ = ABCMeta

	@abstractmethod
	def serialize(self, obj, *args, **kwargs):
		return {}

	@abstractmethod
	def deserialize(self, data, *args, **kwargs):
		return None

class PlayerSerializer(AbstractSerializer):
	instance = None
	@classmethod
	def getInstance(cls):
		if None != cls.instance:
			return cls.instance
		return PlayerSerializer()

	def serialize(self, obj):
		if None == obj:
			return None
		return {"playerId" : obj.playerId}

	def deserialize(self, data):
		if None == data:
			return None
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

	def serialize(self, obj):
		if None == obj:
			return None
		return {"players" : self._serializePlayers(obj._players),
				"scoreTracker" : self.scoreTrackerSerializer.serialize(obj._scoreTracker),
				"curSequence" : self.sequenceSerializer.serialize(obj._curSequence)}

	def _serializePlayers(self, players):
		serializedPlayers = []
		for player in players:
			serializedPlayers.append(self.playerSerializer.serialize(player))
		return serializedPlayers

	def deserialize(self, data):
		if None == data:
			return None
		players = self._deserializePlayers(data["players"])
		scoreTracker = self.scoreTrackerSerializer.deserialize(data["scoreTracker"], players)
		game = euchre.Game(players, scoreTracker, euchre.SequenceFactory.getInstance())
		game._curSequence = self.sequenceSerializer.deserialize(data["curSequence"], players)
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

	def serialize(self, obj):
		if None == obj:
			return None
		return {"teams" : obj._teams,
				"scores" : obj._teamScores}

	def deserialize(self, data, players):
		if None == data:
			return None
		scoreTracker = euchre.ScoreTracker.getInstance(players, data["teams"])
		scoreTracker._teamScores = data["scores"]
		return scoreTracker

class SequenceSerializer(AbstractSerializer):
	instance = None
	@classmethod
	def getInstance(cls):
		if None != cls.instance:
			return cls.instance
		return SequenceSerializer(TrumpSelectorSerializer.getInstance(), RoundSerializer.getInstance(), CardSerializer.getInstance())

	def __init__(self, trumpSelectorSerializer, roundSerializer, cardSerializer):
		self.trumpSelectorSerializer = trumpSelectorSerializer
		self.roundSerializer = roundSerializer
		self.cardSerializer = cardSerializer

	def serialize(self, obj):
		if None == obj:
			return None
		return {"trumpSelector" : self.trumpSelectorSerializer.serialize(obj._trumpSelector),
				"round" : self.roundSerializer.serialize(obj._round),
				"upCard" : self.cardSerializer.serialize(obj._upCard)}

	def deserialize(self, data, players):
		if None == data:
			return None
		trumpSelector = self.trumpSelectorSerializer.deserialize(data["trumpSelector"], players)
		round = self.roundSerializer.deserialize(data["round"], players)
		upCard = self.cardSerializer.deserialize(data["upCard"])
		return euchre.Sequence(trumpSelector, round, upCard)

class TrumpSelectorSerializer(AbstractSerializer):
	instance = None
	@classmethod
	def getInstance(cls):
		if None != cls.instance:
			return cls.instance
		return TrumpSelectorSerializer(TurnTrackerSerializer.getInstance())

	def __init__(self, turnTrackerSerializer):
		self.turnTrackerSerializer = turnTrackerSerializer

	def serialize(self, obj):
		if None == obj:
			return None
		selectingPlayerId = obj._selectingPlayerId
		if None == selectingPlayerId:
			selectingPlayerId = ""
		return {"turnTracker" : self.turnTrackerSerializer.serialize(obj._turnTracker),
				"availableTrump" : obj._availableTrump,
				"selectedTrump" : obj._selectedTrump,
				"selectingPlayerId" : selectingPlayerId}

	def deserialize(self, data, players):
		if None == data:
			return None
		selectingPlayerId = data["selectingPlayerId"]
		if "" == selectingPlayerId:
			selectingPlayerId = None
		turnTracker = self.turnTrackerSerializer.deserialize(data["turnTracker"], players)
		trumpSelector = euchre.TrumpSelector(turnTracker, data["availableTrump"])
		trumpSelector._selectedTrump = data["selectedTrump"]
		trumpSelector._selectingPlayerId = selectingPlayerId
		return trumpSelector

class RoundSerializer(AbstractSerializer):
	instance = None
	@classmethod
	def getInstance(cls):
		if None != cls.instance:
			return cls.instance
		return RoundSerializer(TrickEvaluatorSerializer.getInstance(), TurnTrackerSerializer.getInstance(), TrickSerializer.getInstance(), CardSerializer.getInstance())

	def __init__(self, trickEvaluatorSerializer, turnTrackerSerializer, trickSerializer, cardSerializer):
		self.trickEvaluatorSerializer = trickEvaluatorSerializer
		self.turnTrackerSerializer = turnTrackerSerializer
		self.trickSerializer = trickSerializer
		self.cardSerializer = cardSerializer

	def serialize(self, obj):
		if None == obj:
			return None
		return {"turnTracker" : self.turnTrackerSerializer.serialize(obj._turnTracker),
				"trickEvaluator" : self.trickEvaluatorSerializer.serialize(obj._trickEvaluator),
				"hands" : self._serializeHands(obj.hands),
				"curTrick" : self.trickSerializer.serialize(obj.curTrick),
				"prevTricks" : self._serializeTricks(obj.prevTricks),
				"scores" : self._serializeScores(obj._scores)}

	def _serializeHands(self, hands):
		serializedHands = {}
		for playerId, hand in hands.iteritems():
			serializedHands[playerId] = self._serializeHand(hand)
		return serializedHands

	def _serializeHand(self, hand):
		serializedHand = []
		for card in hand:
			serializedHand.append(self.cardSerializer.serialize(card))
		return serializedHand

	def _serializeTricks(self, tricks):
		serializedTricks = []
		for trick in tricks:
			serializedTricks.append(self.trickSerializer.serialize(trick))
		return serializedTricks

	def _serializeScores(self, scores):
		return scores

	def deserialize(self, data, players):
		if None == data:
			return None
		trickEvaluator = self.trickEvaluatorSerializer.deserialize(data["trickEvaluator"])
		turnTracker = self.turnTrackerSerializer.deserialize(data["turnTracker"], players)
		hands = self._deserializeHands(data["hands"])
		round = euchre.Round(turnTracker, trickEvaluator, hands)
		round.curTrick = self.trickSerializer.deserialize(data["curTrick"])
		round.prevTricks = self._deserializeTricks(data["prevTricks"])
		round._scores = self._deserializeScores(data["scores"])
		return round

	def _deserializeHands(self, hands):
		deserializedHands = {}
		for playerId, hand in hands.iteritems():
			deserializedHands[playerId] = self._deserializeHand(hand)
		return deserializedHands

	def _deserializeHand(self, hand):
		deserializedHand = []
		for card in hand:
			deserializedHand.append(self.cardSerializer.deserialize(card))
		return deserializedHand

	def _deserializeTricks(self, tricks):
		deserializedTricks = []
		for trick in tricks:
			deserializedTricks.append(self.trickSerializer.deserialize(trick))
		return deserializedTricks

	def _deserializeScores(self, scores):
		return scores

class TurnTrackerSerializer(AbstractSerializer):
	instance = None
	@classmethod
	def getInstance(cls):
		if None != cls.instance:
			return cls.instance
		return TurnTrackerSerializer()

	def serialize(self, obj):
		if None == obj:
			return None
		return {"currentIndex" : obj._currentIndex,
				"allTurnCount" : obj._allTurnCount}

	def deserialize(self, data, players):
		if None == data:
			return None
		turnTracker = game.TurnTracker.getInstance(players)
		turnTracker._currentIndex = data["currentIndex"]
		turnTracker._allTurnCount = data["allTurnCount"]
		return turnTracker

class TrickEvaluatorSerializer(AbstractSerializer):
	instance = None
	@classmethod
	def getInstance(cls):
		if None != cls.instance:
			return cls.instance
		return TrickEvaluatorSerializer()

	def serialize(self, obj):
		if None == obj:
			return None
		return {"trumpSuit" : obj._trumpSuit}

	def deserialize(self, data):
		if None == data:
			return None
		return euchre.TrickEvaluator.getInstance(data["trumpSuit"])

class TrickSerializer(AbstractSerializer):
	instance = None
	@classmethod
	def getInstance(cls):
		if None != cls.instance:
			return cls.instance
		return TrickSerializer(CardSerializer.getInstance())

	def __init__(self, cardSerializer):
		self.cardSerializer = cardSerializer

	def serialize(self, obj):
		if None == obj:
			return None
		return {"ledSuit" : obj.ledSuit,
				"playedCards" : self._serializePlayedCards(obj.playedCards)}

	def _serializePlayedCards(self, cards):
		serializedCards = {}
		for playerId, card in cards.iteritems():
			serializedCards[playerId] = self.cardSerializer.serialize(card)
		return serializedCards

	def deserialize(self, data):
		if None == data:
			return None
		trick = euchre.Trick.getInstance()
		trick.ledSuit = data["ledSuit"]
		trick.playedCards = self._deserializePlayedCards(data["playedCards"])
		return trick

	def _deserializePlayedCards(self, playedCards):
		deserializedCards = {}
		for playerId, card in playedCards.iteritems():
			deserializedCards[playerId] = self.cardSerializer.deserialize(card)
		return deserializedCards

class CardSerializer(AbstractSerializer):
	instance = None
	@classmethod
	def getInstance(cls):
		if None != cls.instance:
			return cls.instance
		return CardSerializer()

	def serialize(self, obj):
		if None == obj:
			return None
		return {"suit" : obj.suit,
				"value" : obj.value}

	def deserialize(self, data):
		if None == data:
			return None
		return euchre.Card.getInstance(data["suit"], data["value"])
