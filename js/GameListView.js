if (AVOCADO == undefined) {
	var AVOCADO = {};
}

AVOCADO.GameListView = function(gameLister, templateRenderer, gameListDiv, jqueryWrapper, viewManager, gameCreator, gameListElementBuilder) {
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
			var element = gameListElementBuilder.buildListElement(response.games[i], self.showGameData, true);
			element.appendTo(gameListDiv);
		}

		var menuHtml = templateRenderer.renderTemplate("gameListMenu");
		var menu = jqueryWrapper.getElement(menuHtml);
		menu.find(".gameCreatorContainer").append(gameCreator.buildGameCreator());
		gameListDiv.append(menu);

		gameListDiv.show();
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
	var gameCreator = AVOCADO.GameCreatorBuilder.getInstance(facebook, ajax, viewManager, templateRenderer, jqueryWrapper, locStrings);
	var gameListElementBuilder = AVOCADO.GameListElementBuilder.getInstance(jqueryWrapper, templateRenderer, locStrings, playerNameDirectory, facebook);
	return new AVOCADO.GameListView(gameLister, templateRenderer, gameListDiv, jqueryWrapper, viewManager, gameCreator, gameListElementBuilder);
};
