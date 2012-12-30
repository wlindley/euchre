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
		for (var i = 0; i < response.hand.length; i++) {
			var card = response.hand[i];
			cardsHtml += templateRenderer.renderTemplate("card", {"suit" : card.suit, "value" : card.value});
		}
		var handHtml = templateRenderer.renderTemplate("hand", {"hand" : cardsHtml});

		var turn = locStrings.yourTurn;
		if (fbId != response.currentPlayerId) {
			turn = locStrings.otherTurn.replace("%playerId%", response.currentPlayerId);
		}

		var trumpSelectionElement = trumpSelectionAreaBuilder.buildTrumpSelectionArea(response.upCard, response.status, response.gameId, response.dealerId, response.currentPlayerId);
		var roundPlayingElement = roundPlayingAreaBuilder.buildRoundPlayingArea(response.status, response.ledSuit, response.currentTrick);
		var gameHtml = templateRenderer.renderTemplate("game", {"gameId" : response.gameId, "hand" : handHtml, "turn" : turn});
		var gameElement = jqueryWrapper.getElement(gameHtml);
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
	var roundPlayingAreaBuilder = AVOCADO.RoundPlayingAreaBuilder.getInstance(templateRenderer, jqueryWrapper, locStrings);
	return new AVOCADO.GamePlayView(ajax, fbId, templateRenderer, gamePlayDiv, viewManager, locStrings, trumpSelectionAreaBuilder, jqueryWrapper, roundPlayingAreaBuilder);
};
