if (AVOCADO == undefined) {
	var AVOCADO = {};
}

AVOCADO.GamePlayView = function(ajax, fbId, templateRenderer, gamePlayView) {
	var self = this;

	this.show = function(gameId) {
		ajax.call("getGameData", {"gameId" : gameId, "playerId" : fbId}, handleGetGameDataResponse);
	};

	function handleGetGameDataResponse(response) {
		var cardsHtml = "";
		for (var i = 0; i < response.hand.length; i++) {
			var card = response.hand[i];
			cardsHtml += templateRenderer.renderTemplate("card", {"suit" : card.suit, "value" : card.value});
		}
		var handHtml = templateRenderer.renderTemplate("hand", {"hand" : cardsHtml});
		var gameHtml = templateRenderer.renderTemplate("game", {"gameId" : response.gameId, "hand" : handHtml});
		gamePlayView.html(gameHtml);
		gamePlayView.show();
	}
};

AVOCADO.GamePlayView.getInstance = function(ajax, fbId, templateRenderer, gamePlayView) {
	return new AVOCADO.GamePlayView(ajax, fbId, templateRenderer, gamePlayView);
};
