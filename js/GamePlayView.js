if (AVOCADO == undefined) {
	var AVOCADO = {};
}

AVOCADO.GamePlayView = function(ajax, fbId, templateRenderer, gamePlayDiv, viewManager, locStrings, trumpSelectionAreaBuilder) {
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
		var trumpSelectionHtml = trumpSelectionAreaBuilder.buildTrumpSelectionArea(response.upCard);
		var gameHtml = templateRenderer.renderTemplate("game", {"gameId" : response.gameId, "hand" : handHtml, "turn" : turn, "trumpSelection" : trumpSelectionHtml});
		gamePlayDiv.html(gameHtml);
		gamePlayDiv.find(".viewGameList").click(self.handleViewGameListClick);
		gamePlayDiv.show();
	}

	this.handleViewGameListClick = function(event) {
		viewManager.showView("gameList");
	};
};

AVOCADO.GamePlayView.getInstance = function(ajax, fbId, templateRenderer, gamePlayDiv, viewManager, locStrings) {
	return new AVOCADO.GamePlayView(ajax, fbId, templateRenderer, gamePlayDiv, viewManager, locStrings, AVOCADO.TrumpSelectionAreaBuilder.getInstance(templateRenderer));
};
