if (AVOCADO == undefined) {
	var AVOCADO = {};
}

AVOCADO.GamePlayView = function(ajax, fbId, templateRenderer, gamePlayDiv, viewManager, locStrings, trumpSelectionAreaBuilder, jqueryWrapper, roundPlayingAreaBuilder) {
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

		var turn = locStrings.yourTurn;
		if (fbId != response.round.currentPlayerId) {
			turn = locStrings.otherTurn.replace("%playerId%", response.round.currentPlayerId);
		}

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

		var trumpSelectionElement = trumpSelectionAreaBuilder.buildTrumpSelectionArea(response.round.upCard, response.status, response.gameId, response.round.dealerId, response.round.currentPlayerId);

		var gameHtml = templateRenderer.renderTemplate("game", {"gameId" : response.gameId, "hand" : handHtml, "turn" : turn, "gameScores" : gameScoresHtml, "roundScores" : roundScoresHtml, "trump" : trumpText});
		var gameElement = jqueryWrapper.getElement(gameHtml);

		var cardElements = gameElement.find(".card");
		var roundPlayingElement = roundPlayingAreaBuilder.buildRoundPlayingArea(response.status, response.round.currentTrick.ledSuit, response.round.currentTrick.playedCards, cardElements, response.gameId, response.round.currentPlayerId, response.round.currentTrick.leaderId, response.teams);

		var trumpSelectionInsertionPoint = gameElement.find(".trumpSelection");
		trumpSelectionInsertionPoint.append(trumpSelectionElement);
		var roundPlayingInsertionPoint = gameElement.find(".playingRound");
		roundPlayingInsertionPoint.append(roundPlayingElement);

		gamePlayDiv.append(gameElement);
		gamePlayDiv.find(".viewGameList").click(self.handleViewGameListClick);
		gamePlayDiv.show();
	}

	this.handleViewGameListClick = function(event) {
		viewManager.showView("gameList");
	};
};

AVOCADO.GamePlayView.getInstance = function(ajax, fbId, templateRenderer, gamePlayDiv, viewManager, locStrings, jqueryWrapper) {
	var trumpSelectionAreaBuilder = AVOCADO.TrumpSelectionAreaBuilder.getInstance(templateRenderer, jqueryWrapper, ajax, fbId, locStrings, viewManager);
	var roundPlayingAreaBuilder = AVOCADO.RoundPlayingAreaBuilder.getInstance(templateRenderer, jqueryWrapper, locStrings, ajax, fbId, viewManager);
	return new AVOCADO.GamePlayView(ajax, fbId, templateRenderer, gamePlayDiv, viewManager, locStrings, trumpSelectionAreaBuilder, jqueryWrapper, roundPlayingAreaBuilder);
};
