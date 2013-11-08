if (AVOCADO == undefined) {
	var AVOCADO = {};
}

AVOCADO.GamePlayView = function(ajax, fbId, templateRenderer, gamePlayDiv, viewManager, locStrings, trumpSelectionAreaBuilder, jqueryWrapper, roundPlayingAreaBuilder, discardAreaBuilder, previousTrickDisplayBuilder, playerNameDirectory, gameCompleteDisplayBuilder) {
	var self = this;

	this.init = function() {
		viewManager.registerView("gamePlay", self);
	};

	this.show = function(params) {
		ajax.call("getGameData", {"gameId" : params.gameId, "playerId" : fbId}, handleGetGameDataResponse);
	};

	this.hide = function() {
		gamePlayDiv.hide();
	};

	function handleGetGameDataResponse(response) {
		gamePlayDiv.empty();

		var cardsHtml = "";
		for (var i = 0; i < response.round.hand.length; i++) {
			var card = response.round.hand[i];
			cardsHtml += templateRenderer.renderTemplate("card", {"suit" : card.suit, "value" : card.value});
		}
		var handHtml = templateRenderer.renderTemplate("hand", {"hand" : cardsHtml});

		var gameScores = response.scores;
		var roundScores = response.round.tricksTaken;
		if (0 <= response.teams[1].indexOf(fbId)) {
			gameScores = [response.scores[1], response.scores[0]];
			roundScores = [response.round.tricksTaken[1], response.round.tricksTaken[0]];
		}
		var gameScoresHtml = templateRenderer.renderTemplate("gameScores", {"yourScore" : gameScores[0], "otherScore" : gameScores[1]});
		var roundScoresHtml = templateRenderer.renderTemplate("roundScores", {"yourScore" : roundScores[0], "otherScore" : roundScores[1]});

		var trumpText = "";
		if (0 < response.round.trump) {
			trumpText = locStrings.trumpDisplay.replace("%trumpSuit%", locStrings["suit_" + response.round.trump]);
		}

		var gameHtml = templateRenderer.renderTemplate("game", {"gameId" : response.gameId, "hand" : handHtml, "gameScores" : gameScoresHtml, "roundScores" : roundScoresHtml, "trump" : trumpText});
		var gameElement = jqueryWrapper.getElement(gameHtml);
		gameElement.find(".hand").find(".card").addClass("handElement");

		if (null !== response.round.currentPlayerId && undefined !== response.round.currentPlayerId) {
			var namePromise = playerNameDirectory.getNamePromise(response.round.currentPlayerId);
			namePromise.registerForUpdates(gameElement.find(".turn").find(".playerName"));
		}

		var cardElements = gameElement.find(".card");

		if ("complete" == response.status) {
			var gameCompleteElement = gameCompleteDisplayBuilder.buildGameCompleteDisplay(response.teams, response.scores);

			var gameCompleteInsertionPoint = gameElement.find(".gameCompleteWrapper");
			gameCompleteInsertionPoint.append(gameCompleteElement);
		} else {
			var trumpSelectionElement = trumpSelectionAreaBuilder.buildTrumpSelectionArea(response.round.upCard, response.status, response.gameId, response.round.dealerId, response.round.currentPlayerId, response.teams);
			var roundPlayingElement = roundPlayingAreaBuilder.buildRoundPlayingArea(response.status, response.round.currentTrick.ledSuit, response.round.currentTrick.playedCards, cardElements, response.gameId, response.round.currentPlayerId, response.round.currentTrick.leaderId, response.teams);
			var discardElement = discardAreaBuilder.buildDiscardArea(response.status, cardElements, response.gameId, response.round.currentPlayerId);

			var trumpSelectionInsertionPoint = gameElement.find(".trumpSelection");
			trumpSelectionInsertionPoint.append(trumpSelectionElement);
			var roundPlayingInsertionPoint = gameElement.find(".playingRound");
			roundPlayingInsertionPoint.append(roundPlayingElement);
			var discardInsertionPoint = gameElement.find(".discard");
			discardInsertionPoint.append(discardElement);
		}

		var previousTrickElement = previousTrickDisplayBuilder.buildPreviousTrickDisplay(response.previousTrick.playedCards, response.previousTrick.winnerId);
		var previousTrickInsertionPoint = gameElement.find(".previousTrickWrapper");
		previousTrickInsertionPoint.append(previousTrickElement);

		gamePlayDiv.append(gameElement);
		gamePlayDiv.find(".viewGameList").click(self.handleViewGameListClick);
		gamePlayDiv.show();
	}

	this.handleViewGameListClick = function(event) {
		viewManager.showView("gameList");
	};
};

AVOCADO.GamePlayView.getInstance = function(ajax, fbId, templateRenderer, gamePlayDiv, viewManager, locStrings, jqueryWrapper, playerNameDirectory) {
	var trumpSelectionAreaBuilder = AVOCADO.TrumpSelectionAreaBuilder.getInstance(templateRenderer, jqueryWrapper, ajax, fbId, locStrings, viewManager, playerNameDirectory);
	var roundPlayingAreaBuilder = AVOCADO.RoundPlayingAreaBuilder.getInstance(templateRenderer, jqueryWrapper, locStrings, ajax, fbId, viewManager, playerNameDirectory);
	var discardAreaBuilder = AVOCADO.DiscardAreaBuilder.getInstance(templateRenderer, jqueryWrapper, locStrings, ajax, fbId, viewManager);
	var previousTrickDisplayBuilder = AVOCADO.PreviousTrickDisplayBuilder.getInstance(templateRenderer, jqueryWrapper, playerNameDirectory, fbId);
	var gameCompleteDisplayBuilder = AVOCADO.GameCompleteDisplayBuilder.getInstance(templateRenderer, jqueryWrapper, locStrings, playerNameDirectory, fbId);
	return new AVOCADO.GamePlayView(ajax, fbId, templateRenderer, gamePlayDiv, viewManager, locStrings, trumpSelectionAreaBuilder, jqueryWrapper, roundPlayingAreaBuilder, discardAreaBuilder, previousTrickDisplayBuilder, playerNameDirectory, gameCompleteDisplayBuilder);
};
