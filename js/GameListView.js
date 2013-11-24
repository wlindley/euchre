if (AVOCADO == undefined) {
	var AVOCADO = {};
}

AVOCADO.GameListView = function(gameLister, templateRenderer, gameListDiv, jqueryWrapper, viewManager, ajax, locStrings, facebook, gameCreator, gameJoiner, playerNameDirectory, gameListElementBuilder) {
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
		gameListDiv.append(templateRenderer.renderTemplate("gameListHeader"));
		for (var i = 0; i < response.games.length; i++) {
			var element = gameListElementBuilder.buildListElement(response.games[i], self.showGameData);
			element.appendTo(gameListDiv);
		}

		var gameCreatorElement = gameCreator.buildGameCreator();
		gameListDiv.append(gameCreatorElement);

		var gameJoinerElement = gameJoiner.buildGameJoiner();
		gameListDiv.append(gameJoinerElement);

		gameListDiv.show();
	}

	function buildTemplateValues(gameData) {
		var values = {
			"gameId" : gameData.gameId,
			"status" : locStrings[gameData.status],
			"vs" : locStrings["vs"]
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

AVOCADO.GameListView.getInstance = function(templateRenderer, gameListDiv, jqueryWrapper, viewManager, ajax, locStrings, facebook, playerNameDirectory) {
	var gameLister = AVOCADO.GameLister.getInstance(facebook, ajax);
	var gameCreator = AVOCADO.GameCreatorBuilder.getInstance(facebook, ajax, viewManager, templateRenderer, jqueryWrapper);
	var gameJoiner = AVOCADO.GameJoinerBuilder.getInstance(facebook, ajax, viewManager, templateRenderer, jqueryWrapper);
	var gameListElementBuilder = AVOCADO.GameListElementBuilder.getInstance(jqueryWrapper, templateRenderer, locStrings, playerNameDirectory, facebook);
	return new AVOCADO.GameListView(gameLister, templateRenderer, gameListDiv, jqueryWrapper, viewManager, ajax, locStrings, facebook, gameCreator, gameJoiner, playerNameDirectory, gameListElementBuilder);
};
