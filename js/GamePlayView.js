if (AVOCADO == undefined) {
	var AVOCADO = {};
}

AVOCADO.GamePlayView = function(ajax, facebook, templateRenderer, gamePlayDiv, viewManager, locStrings, trumpSelectionAreaBuilder, jqueryWrapper, roundPlayingAreaBuilder, discardAreaBuilder, previousTrickDisplayBuilder, playerNameDirectory, gameCompleteDisplayBuilder, teamUtils) {
	var self = this;

	this.init = function() {
		viewManager.registerView("gamePlay", self);
	};

	this.show = function(params) {
		ajax.call("getGameData", {"gameId" : params.gameId, "playerId" : facebook.getSignedInPlayerId()}).done(handleGetGameDataResponse);
	};

	this.hide = function() {
		gamePlayDiv.hide();
	};

	function handleGetGameDataResponse(response) {
		gamePlayDiv.empty();

		var gameElement = buildGameElement(response);
		displayCurrentPlayer(gameElement, response.teams, response.round.currentPlayerId);
		showGameStatusAppropriateActionArea(gameElement, response);
		showPreviousTrick(gameElement, response);

		gamePlayDiv.append(gameElement);
		gamePlayDiv.find(".viewGameList").click(self.handleViewGameListClick);
		gamePlayDiv.show();
	}

	this.handleViewGameListClick = function(event) {
		viewManager.showView("gameList");
	};

	function buildHand(response) {
		var cardsHtml = "";
		for (var i = 0; i < response.round.hand.length; i++) {
			var card = response.round.hand[i];
			cardsHtml += templateRenderer.renderTemplate("card", {"suit" : card.suit, "value" : card.value});
		}
		return templateRenderer.renderTemplate("hand", {"hand" : cardsHtml});
	}

	function buildGameScores(response) {
		var gameScores = response.scores;
		if (teamUtils.isLocalPlayerOnTeam(response.teams[1])) {
			return templateRenderer.renderTemplate("gameScores", {"yourScore" : gameScores[1], "otherScore" : gameScores[0]});
		}
		return templateRenderer.renderTemplate("gameScores", {"yourScore" : gameScores[0], "otherScore" : gameScores[1]});
	}

	function buildRoundScores(response) {
		var roundScores = response.round.tricksTaken;
		if (teamUtils.isLocalPlayerOnTeam(response.teams[1])) {
			return templateRenderer.renderTemplate("roundScores", {"yourScore" : roundScores[1], "otherScore" : roundScores[0]});
		}
		return templateRenderer.renderTemplate("roundScores", {"yourScore" : roundScores[0], "otherScore" : roundScores[1]});
	}

	function buildTrumpString(response) {
		var trumpString = locStrings["suit_" + response.round.trump];
		if (undefined === trumpString) {
			trumpString = locStrings["n/a"];
		}
		return trumpString;
	}

	function buildGameElement(response) {
		var handHtml = buildHand(response);
		var gameScoresHtml = buildGameScores(response);
		var roundScoresHtml = buildRoundScores(response);
		var trumpString = buildTrumpString(response);
		var gameHtml = templateRenderer.renderTemplate("game", {"hand" : handHtml, "gameScores" : gameScoresHtml, "roundScores" : roundScoresHtml, "trump" : trumpString, "status" : locStrings[response.status]});
		return jqueryWrapper.getElement(gameHtml);
	}

	function displayCurrentPlayer(gameElement, teams, currentPlayerId) {
		var nameElement = gameElement.find(".turn").find(".playerName");
		if (null !== currentPlayerId && undefined !== currentPlayerId) {
			var namePromise = playerNameDirectory.getNamePromise(currentPlayerId);
			namePromise.registerForUpdates(nameElement);
			nameElement.addClass(teamUtils.getClassForPlayer(teams, currentPlayerId));
		} else {
			nameElement.text(locStrings["n/a"]);
		}
	}

	function showGameStatusAppropriateActionArea(gameElement, response) {
		var cardElements = gameElement.find(".card");
		if ("complete" == response.status) {
			var gameCompleteElement = gameCompleteDisplayBuilder.buildGameCompleteDisplay(response.teams, response.scores, response.gameId);

			var gameCompleteInsertionPoint = gameElement.find(".gameCompleteWrapper");
			gameCompleteInsertionPoint.append(gameCompleteElement);

			gameElement.find(".hand").hide();
		} else {
			var trumpSelectionElement = trumpSelectionAreaBuilder.buildTrumpSelectionArea(response.round.upCard, response.status, response.gameId, response.round.dealerId, response.round.currentPlayerId, response.teams, response.round.blackListedSuits);
			var roundPlayingElement = roundPlayingAreaBuilder.buildRoundPlayingArea(response.status, response.round.currentTrick.ledSuit, response.round.currentTrick.playedCards, cardElements, response.gameId, response.round.currentPlayerId, response.round.currentTrick.leaderId, response.teams);
			var discardElement = discardAreaBuilder.buildDiscardArea(response.status, cardElements, response.gameId, response.round.currentPlayerId);

			var trumpSelectionInsertionPoint = gameElement.find(".trumpSelection");
			trumpSelectionInsertionPoint.append(trumpSelectionElement);
			var roundPlayingInsertionPoint = gameElement.find(".playingRound");
			roundPlayingInsertionPoint.append(roundPlayingElement);
			var discardInsertionPoint = gameElement.find(".discard");
			discardInsertionPoint.append(discardElement);
		}
	}

	function showPreviousTrick(gameElement, response) {
		var previousTrickElement = previousTrickDisplayBuilder.buildPreviousTrickDisplay(response.previousTrick.playedCards, response.previousTrick.winnerId, response.teams);
		var previousTrickInsertionPoint = gameElement.find(".previousTrickWrapper");
		previousTrickInsertionPoint.append(previousTrickElement);
	}
};

AVOCADO.GamePlayView.getInstance = function(ajax, facebook, templateRenderer, gamePlayDiv, viewManager, locStrings, jqueryWrapper, playerNameDirectory, teamUtils) {
	var trumpSelectionAreaBuilder = AVOCADO.TrumpSelectionAreaBuilder.getInstance(templateRenderer, jqueryWrapper, ajax, facebook, locStrings, viewManager, playerNameDirectory, teamUtils);
	var roundPlayingAreaBuilder = AVOCADO.RoundPlayingAreaBuilder.getInstance(templateRenderer, jqueryWrapper, locStrings, ajax, facebook, viewManager, playerNameDirectory, teamUtils);
	var discardAreaBuilder = AVOCADO.DiscardAreaBuilder.getInstance(templateRenderer, jqueryWrapper, locStrings, ajax, facebook, viewManager);
	var previousTrickDisplayBuilder = AVOCADO.PreviousTrickDisplayBuilder.getInstance(templateRenderer, jqueryWrapper, playerNameDirectory, facebook, teamUtils);
	var gameCompleteDisplayBuilder = AVOCADO.GameCompleteDisplayBuilder.getInstance(templateRenderer, jqueryWrapper, locStrings, playerNameDirectory, facebook, ajax, viewManager, teamUtils);
	return new AVOCADO.GamePlayView(ajax, facebook, templateRenderer, gamePlayDiv, viewManager, locStrings, trumpSelectionAreaBuilder, jqueryWrapper, roundPlayingAreaBuilder, discardAreaBuilder, previousTrickDisplayBuilder, playerNameDirectory, gameCompleteDisplayBuilder, teamUtils);
};
