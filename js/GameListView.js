if (AVOCADO == undefined) {
	var AVOCADO = {};
}

AVOCADO.GameListView = function(gameLister, templateRenderer, gameListDiv, jqueryWrapper, gamePlayView) {
	var self = this;

	this.show = function() {
		gameLister.getGameList(handleGameListResponse);
	};

	function handleGameListResponse(response) {
		for (var i = 0; i < response.games.length; i++) {
			var element = jqueryWrapper.getElement(templateRenderer.renderTemplate("gameListEntry", buildTemplateValues(response.games[i])));
			element.find(".viewGameData").click(self.showGameData);
			element.appendTo(gameListDiv);
		}
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

	this.showGameData = function(event) {
		gameListDiv.hide();
		var target = jqueryWrapper.getElement(event.currentTarget);
		var gameId = target.attr("id").replace("gameId_", "");
		gamePlayView.show(gameId);
	};
};

AVOCADO.GameListView.getInstance = function(gameLister, templateRenderer, gameListDiv, jqueryWrapper, gamePlayView) {
	return new AVOCADO.GameListView(gameLister, templateRenderer, gameListDiv, jqueryWrapper, gamePlayView);
};
