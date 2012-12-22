if (AVOCADO == undefined) {
	var AVOCADO = {};
}

AVOCADO.GameListView = function(gameLister, templateRenderer, gameListDiv, jqueryWrapper, viewManager) {
	var self = this;

	this.init = function() {
		viewManager.registerView("gameList", self);
	};

	this.show = function() {
		gameLister.getGameList(handleGameListResponse);
	};

	this.hide = function() {
		gameListDiv.hide();
	};

	function handleGameListResponse(response) {
		gameListDiv.empty();
		for (var i = 0; i < response.games.length; i++) {
			var element = jqueryWrapper.getElement(templateRenderer.renderTemplate("gameListEntry", buildTemplateValues(response.games[i])));
			if (response.games[i].status != "waiting_for_more_players") {
				element.find(".viewGameData").click(self.showGameData);
			} else {
				element.removeClass("gameListEntryClickable");
			}
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
		viewManager.showView("gamePlay", {"gameId" : gameId});
	};
};

AVOCADO.GameListView.getInstance = function(gameLister, templateRenderer, gameListDiv, jqueryWrapper, viewManager) {
	return new AVOCADO.GameListView(gameLister, templateRenderer, gameListDiv, jqueryWrapper, viewManager);
};
