if (AVOCADO == undefined) {
	var AVOCADO = {};
}

AVOCADO.GameListView = function(gameLister, templateRenderer, gameListDiv) {
	var self = this;

	this.show = function() {
		gameLister.getGameList(handleGameListResponse);
	};

	function handleGameListResponse(response) {
		var html = "";
		for (var i = 0; i < response.games.length; i++) {
			html += templateRenderer.renderTemplate("gameListEntry", buildTemplateValues(response.games[i]));
		}
		gameListDiv.html(html);
		gameListDiv.show();
	}

	function buildTemplateValues(gameData) {
		var values = {
			"gameId" : gameData.gameId,
			"status" : gameData.status,
			"playerIds" : gameData.playerIds,
			"currentPlayer" : gameData.currentPlayerId,
		};
		return values;
	}
};

AVOCADO.GameListView.getInstance = function(gameLister, templateRenderer, gameListDiv) {
	return new AVOCADO.GameListView(gameLister, templateRenderer, gameListDiv);
};
