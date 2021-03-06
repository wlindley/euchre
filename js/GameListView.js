if (AVOCADO == undefined) {
	var AVOCADO = {};
}

AVOCADO.GameListView = function(gameLister, templateRenderer, rootElement, jqueryWrapper, viewManager, gameListMenuBuilder, gameListElementBuilder, gameInviteLister) {
	var self = this;

	this.init = function() {
		viewManager.registerView("gameList", self);
	};

	this.show = function() {
		rootElement.empty();

		var element = jqueryWrapper.getElement(templateRenderer.renderTemplate("gameList"));
		rootElement.append(element);

		element.find(".gameListMenuContainer").append(gameListMenuBuilder.buildGameMenu());

		gameLister.getGameList().done(handleGameListResponse);
		gameInviteLister.getGameInviteList().done(this.handleGameInviteListResponse);

		rootElement.show();
	};

	this.hide = function() {
		rootElement.hide();
	};

	function handleGameListResponse(response) {
		var gameListElement = rootElement.find(".gameListContainer");
		for (var i = 0; i < response.games.length; i++) {
			var curElement = gameListElementBuilder.buildListElement(response.games[i], undefined);
			gameListElement.append(curElement);
		}
	}

	this.handleGameInviteListResponse = function(invitedGameDatas) {
		var gameListElement = rootElement.find(".gameListContainer");
		for (var i = 0; i < invitedGameDatas.length; i++) {
			var curElement = gameListElementBuilder.buildListElement(invitedGameDatas[i].data, invitedGameDatas[i].requestId);
			gameListElement.prepend(curElement);
		}
	};
};

AVOCADO.GameListView.getInstance = function(templateRenderer, rootElement, jqueryWrapper, viewManager, ajax, locStrings, facebook, playerNameDirectory, dataRetriever, teamUtils) {
	var gameLister = AVOCADO.GameLister.getInstance(facebook, ajax);
	var gameInviteLister = AVOCADO.GameInviteLister.getInstance(facebook, ajax, jqueryWrapper);
	var gameListMenuBuilder = AVOCADO.GameListMenuBuilder.getInstance(facebook, ajax, viewManager, templateRenderer, jqueryWrapper, locStrings);
	var gameListElementBuilder = AVOCADO.GameListElementBuilder.getInstance(jqueryWrapper, templateRenderer, locStrings, playerNameDirectory, facebook, ajax, viewManager, dataRetriever, teamUtils);
	return new AVOCADO.GameListView(gameLister, templateRenderer, rootElement, jqueryWrapper, viewManager, gameListMenuBuilder, gameListElementBuilder, gameInviteLister);
};
