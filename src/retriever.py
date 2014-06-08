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
		return gameObj.getPlayers()[-1].playerId

class HandRetriever(object):
	instance = None
	@classmethod
	def getInstance(cls):
		if None != cls.instance:
			return cls.instance
		return HandRetriever()

	def __init__(self):
		super(HandRetriever, self).__init__()

	def retrieveHand(self, playerId, gameObj):
		sequenceObj = gameObj.getSequence()
		if None == sequenceObj:
			return []
		roundObj = sequenceObj.getRound()
		hands = roundObj.getHands()
		if playerId not in hands:
			return []
		return hands[playerId]

class TurnRetriever(object):
	instance = None
	@classmethod
	def getInstance(cls):
		if None != cls.instance:
			return cls.instance
		return TurnRetriever(HandRetriever.getInstance())

	def __init__(self, handRetriever):
		super(TurnRetriever, self).__init__()
		self._handRetriever = handRetriever

	def retrieveTurn(self, gameObj):
		sequence = gameObj.getSequence()
		if None == sequence:
			return None
		sequenceState = sequence.getState()
		if euchre.Sequence.STATE_TRUMP_SELECTION == sequenceState or euchre.Sequence.STATE_TRUMP_SELECTION_2 == sequenceState:
			return sequence.getTrumpSelector().getTurnTracker().getCurrentPlayerId()
		elif euchre.Sequence.STATE_PLAYING_ROUND == sequenceState:
			return sequence.getRound().getTurnTracker().getCurrentPlayerId()
		elif euchre.Sequence.STATE_DISCARD == sequenceState:
			for player in gameObj.getPlayers():
				hand = self._handRetriever.retrieveHand(player.playerId, gameObj)
				if euchre.Round.MAX_HAND_SIZE < len(hand):
					return player.playerId
		return None

class UpCardRetriever(object):
	instance = None
	@classmethod
	def getInstance(cls):
		if None != cls.instance:
			return cls.instance
		return UpCardRetriever()

	def retrieveUpCard(self, gameObj):
		sequence = gameObj.getSequence()
		if None != sequence and euchre.Sequence.STATE_TRUMP_SELECTION == sequence.getState():
			return sequence.getUpCard()
		return None

class BlackListedSuitsRetriever(object):
	instance = None
	@classmethod
	def getInstance(cls):
		if None != cls.instance:
			return cls.instance
		return BlackListedSuitsRetriever()

	def retrieveBlackListedSuits(self, gameObj):
		sequence = gameObj.getSequence()
		if None != sequence:
			return sequence.getTrumpSelector().getBlackListedSuits()
		return None

class GameStatusRetriever(object):
	instance = None
	@classmethod
	def getInstance(cls, winningScore):
		if None != cls.instance:
			return cls.instance
		return GameStatusRetriever(winningScore)

	def __init__(self, winningScore):
		super(GameStatusRetriever, self).__init__()
		self._winningScore = winningScore

	def retrieveGameStatus(self, gameObj):
		if None == gameObj:
			return "waiting_for_more_players"
		if self._winningScore <= gameObj.getTeamScore(0) or self._winningScore <= gameObj.getTeamScore(1):
			return "complete"
		sequenceState = gameObj.getSequence().getState()
		if euchre.Sequence.STATE_TRUMP_SELECTION == sequenceState:
			return "trump_selection"
		elif euchre.Sequence.STATE_TRUMP_SELECTION_2 == sequenceState:
			return "trump_selection_2"
		elif euchre.Sequence.STATE_PLAYING_ROUND == sequenceState:
			return "round_in_progress"
		elif euchre.Sequence.STATE_DISCARD == sequenceState:
			return "discard"
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
		if None == sequence:
			return None
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
		if None == sequence:
			return {}
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
		if None == sequence:
			return euchre.SUIT_NONE
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
		scores = [0, 0]
		sequence = gameObj.getSequence()
		if None != sequence:
			round = sequence.getRound()
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
		return gameObj.getTeamLists()

class TrickLeaderRetriever(object):
	instance = None
	@classmethod
	def getInstance(cls):
		if None != cls.instance:
			return cls.instance
		return TrickLeaderRetriever(euchre.TrickEvaluator.getInstance())

	def __init__(self, trickEvaluator):
		super(TrickLeaderRetriever, self).__init__()
		self._trickEvaluator = trickEvaluator

	def retrieveTrickLeader(self, gameObj):
		sequence = gameObj.getSequence()
		if None == sequence:
			return None
		round = sequence.getRound()
		trick = round.getCurrentTrick()
		return self.getLeaderFromTrick(trick, round.getTrump())

	def getLeaderFromTrick(self, trick, trump):
		if None == trick:
			return None
		self._trickEvaluator.setTrump(trump)
		return self._trickEvaluator.evaluateTrick(trick)

class PreviousTrickRetriever(object):
	instance = None
	@classmethod
	def getInstance(cls):
		if None != cls.instance:
			return cls.instance
		return PreviousTrickRetriever(TrickLeaderRetriever.getInstance())

	def __init__(self, trickLeaderRetriever):
		super(PreviousTrickRetriever, self).__init__()
		self._trickLeaderRetriever = trickLeaderRetriever

	def retrievePreviousTrick(self, gameObj):
		sequence = gameObj.getSequence()
		tricks = []
		if None != sequence:
			round = sequence.getRound()
			tricks = round.getPreviousTricks()
		if [] == tricks:
			previousSequence = gameObj.getPreviousSequence()	
			if None != previousSequence:
				round = previousSequence.getRound()
				tricks = round.getPreviousTricks()
			else:
				return {}
		trick = tricks[-1]
		playedCards = trick.getPlayedCards()
		return {
			"winnerId" : self._trickLeaderRetriever.getLeaderFromTrick(trick, round.getTrump()),
			"playedCards" : {playerId : {"suit" : playedCards[playerId].suit, "value" : playedCards[playerId].value} for playerId in playedCards}
		}