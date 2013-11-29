if (AVOCADO == undefined) {
	var AVOCADO = {};
}

AVOCADO.GamePlayView = function(ajax, facebook, templateRenderer, gamePlayDiv, viewManager, locStrings, trumpSelectionAreaBuilder, jqueryWrapper, roundPlayingAreaBuilder, discardAreaBuilder, previousTrickDisplayBuilder, playerNameDirectory, gameCompleteDisplayBuilder) {
	var self = this;

	this.init = function() {
		viewManager.registerView("gamePlay", self);
	};

	this.show = function(params) {
		ajax.call("getGameData", {"gameId" : params.gameId, "playerId" : facebook.getSignedInPlayerId()}, handleGetGameDataResponse);
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
		if (0 <= response.teams[1].indexOf(facebook.getSignedInPlayerId())) {
			gameScores = [response.scores[1], response.scores[0]];
			roundScores = [response.round.tricksTaken[1], response.round.tricksTaken[0]];
		}
		var gameScoresHtml = templateRenderer.renderTemplate("gameScores", {"yourScore" : gameScores[0], "otherScore" : gameScores[1]});
		var roundScoresHtml = templateRenderer.renderTemplate("roundScores", {"yourScore" : roundScores[0], "otherScore" : roundScores[1]});

		var trumpString = locStrings["suit_" + response.round.trump];
		if (undefined === trumpString) {
			trumpString = locStrings["n/a"];
		}

		var gameHtml = templateRenderer.renderTemplate("game", {"gameId" : response.gameId, "hand" : handHtml, "gameScores" : gameScoresHtml, "roundScores" : roundScoresHtml, "trump" : trumpString});
		var gameElement = jqueryWrapper.getElement(gameHtml);
		gameElement.find(".hand").find(".card").addClass("handElement");

		if (null !== response.round.currentPlayerId && undefined !== response.round.currentPlayerId) {
			var namePromise = playerNameDirectory.getNamePromise(response.round.currentPlayerId);
			var nameElement = gameElement.find(".turn").find(".playerName");
			namePromise.registerForUpdates(nameElement);
			if ((-1 == response.teams[0].indexOf(facebook.getSignedInPlayerId())) == (-1 == response.teams[0].indexOf(response.round.currentPlayerId))) {
				nameElement.addClass("green");
			} else {
				nameElement.addClass("red");
			}
		} else {
			gameElement.find(".turn").find(".playerName").text(locStrings["n/a"]);
		}

		var cardElements = gameElement.find(".card");

		if ("complete" == response.status) {
			var gameCompleteElement = gameCompleteDisplayBuilder.buildGameCompleteDisplay(response.teams, response.scores, response.gameId);

			var gameCompleteInsertionPoint = gameElement.find(".gameCompleteWrapper");
			gameCompleteInsertionPoint.append(gameCompleteElement);

			gameElement.find(".hand").hide();
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

AVOCADO.GamePlayView.getInstance = function(ajax, facebook, templateRenderer, gamePlayDiv, viewManager, locStrings, jqueryWrapper, playerNameDirectory) {
	var trumpSelectionAreaBuilder = AVOCADO.TrumpSelectionAreaBuilder.getInstance(templateRenderer, jqueryWrapper, ajax, facebook, locStrings, viewManager, playerNameDirectory);
	var roundPlayingAreaBuilder = AVOCADO.RoundPlayingAreaBuilder.getInstance(templateRenderer, jqueryWrapper, locStrings, ajax, facebook, viewManager, playerNameDirectory);
	var discardAreaBuilder = AVOCADO.DiscardAreaBuilder.getInstance(templateRenderer, jqueryWrapper, locStrings, ajax, facebook, viewManager);
	var previousTrickDisplayBuilder = AVOCADO.PreviousTrickDisplayBuilder.getInstance(templateRenderer, jqueryWrapper, playerNameDirectory);
	var gameCompleteDisplayBuilder = AVOCADO.GameCompleteDisplayBuilder.getInstance(templateRenderer, jqueryWrapper, locStrings, playerNameDirectory, facebook, ajax, viewManager);
	return new AVOCADO.GamePlayView(ajax, facebook, templateRenderer, gamePlayDiv, viewManager, locStrings, trumpSelectionAreaBuilder, jqueryWrapper, roundPlayingAreaBuilder, discardAreaBuilder, previousTrickDisplayBuilder, playerNameDirectory, gameCompleteDisplayBuilder);
};
