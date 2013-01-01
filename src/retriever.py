import euchre
import logging

logging.getLogger().setLevel(logging.DEBUG)

class DealerRetriever(object):
	instance = None
	@classmethod
	def getInstance(cls):
		if None != cls.instance:
			return cls.instance
		return DealerRetriever()

	def retrieveDealer(self, gameObj):
		return gameObj.getPlayers()[0].playerId

class HandRetriever(object):
	instance = None
	@classmethod
	def getInstance(cls):
		if None != cls.instance:
			return cls.instance
		return HandRetriever()

	def __init__(self):
		super(HandRetriever, self).__init__()

	def getHand(self, playerId, gameObj):
		sequenceObj = gameObj.getSequence()
		if None == sequenceObj:
			return []
		roundObj = sequenceObj.getRound()
		if playerId not in roundObj.hands:
			return []
		return roundObj.hands[playerId]

class TurnRetriever(object):
	instance = None
	@classmethod
	def getInstance(cls):
		if None != cls.instance:
			return cls.instance
		return TurnRetriever()

	def retrieveTurn(self, gameObj):
		sequence = gameObj.getSequence()
		if None == sequence:
			return None
		if euchre.Sequence.STATE_TRUMP_SELECTION == sequence.getState() or euchre.Sequence.STATE_TRUMP_SELECTION_2 == sequence.getState():
			turnTracker = sequence.getTrumpSelector().getTurnTracker()
		elif euchre.Sequence.STATE_PLAYING_ROUND == sequence.getState():
			turnTracker = sequence.getRound().getTurnTracker()
		else:
			return None
		return turnTracker.getCurrentPlayerId()

class UpCardRetriever(object):
	instance = None
	@classmethod
	def getInstance(cls):
		if None != cls.instance:
			return cls.instance
		return UpCardRetriever()

	def retrieveUpCard(self, gameObj):
		sequence = gameObj.getSequence()
		if euchre.Sequence.STATE_TRUMP_SELECTION == sequence.getState():
			return sequence.getUpCard()
		return None

class GameStatusRetriever(object):
	instance = None
	@classmethod
	def getInstance(cls):
		if None != cls.instance:
			return cls.instance
		return GameStatusRetriever()

	def retrieveGameStatus(self, gameObj):
		if None == gameObj:
			return "waiting_for_more_players"
		sequenceState = gameObj.getSequence().getState()
		if euchre.Sequence.STATE_TRUMP_SELECTION == sequenceState:
			return "trump_selection"
		elif euchre.Sequence.STATE_TRUMP_SELECTION_2 == sequenceState:
			return "trump_selection_2"
		elif euchre.Sequence.STATE_PLAYING_ROUND == sequenceState:
			return "round_in_progress"
		return ""

class LedSuitRetriever(object):
	instance = None
	@classmethod
	def getInstance(cls):
		if None != cls.instance:
			return cls.instance
		return LedSuitRetriever()

	def retrieveLedSuit(self, gameObj):
		sequence = gameObj.getSequence()
		round = sequence.getRound()
		trick = round.getCurrentTrick()
		if None == trick:
			return None
		return trick.getLedSuit()

class CurrentTrickRetriever(object):
	instance = None
	@classmethod
	def getInstance(cls):
		if None != cls.instance:
			return cls.instance
		return CurrentTrickRetriever()

	def retrieveCurrentTrick(self, gameObj):
		sequence = gameObj.getSequence()
		round = sequence.getRound()
		trick = round.getCurrentTrick()
		if None == trick:
			return {}
		playedCards = trick.getPlayedCards()
		return  {playerId : {"suit" : playedCards[playerId].suit, "value" : playedCards[playerId].value} for playerId in playedCards}

class TrumpRetriever(object):
	instance = None
	@classmethod
	def getInstance(cls):
		if None != cls.instance:
			return cls.instance
		return TrumpRetriever()

	def retrieveTrump(self, gameObj):
		sequence = gameObj.getSequence()
		round = sequence.getRound()
		return round.getTrump()

class ScoreRetriever(object):
	instance = None
	@classmethod
	def getInstance(cls):
		if None != cls.instance:
			return cls.instance
		return ScoreRetriever(TeamRetriever.getInstance())

	def __init__(self, teamRetriever):
		super(ScoreRetriever, self).__init__()
		self._teamRetriever = teamRetriever

	def retrieveGameScores(self, gameObj):
		return [gameObj.getTeamScore(0), gameObj.getTeamScore(1)]

	def retrieveRoundScores(self, gameObj):
		sequence = gameObj.getSequence()
		round = sequence.getRound()
		scores = [0, 0]
		for player in gameObj.getPlayers():
			playerTeam = self._teamRetriever.retrieveTeamByPlayerId(gameObj, player.playerId)
			scores[playerTeam] += round.getScore(player.playerId)
		return scores

class TeamRetriever(object):
	instance = None
	@classmethod
	def getInstance(cls):
		if None != cls.instance:
			return cls.instance
		return TeamRetriever()

	def retrieveTeamByPlayerId(self, gameObj, playerId):
		return gameObj.getTeamFromPlayerId(playerId)

	def retrieveTeamLists(self, gameObj):
		teamLists = gameObj.getTeamLists()
		result = []
		for teamList in teamLists:
			result.append([player.playerId for player in teamList])
		return result
