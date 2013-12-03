if (AVOCADO == undefined) {
	var AVOCADO = {};
}

AVOCADO.GameListMenuBuilder = function(facebook, ajax, viewManager, templateRenderer, jqueryWrapper, locStrings) {
	var self = this;

	this.buildGameMenu = function() {
		var element = jqueryWrapper.getElement(templateRenderer.renderTemplate("gameListMenu"));
		element.find(".createGameButton").click(self.createGameClickHandler);
		return element;
	};

	this.createGameClickHandler = function() {
		var params = {
			"playerId" : facebook.getSignedInPlayerId(),
			"team" : 0
		};
		ajax.call("createGame", params).done(handleCreateGameResponse);
	};

	function handleCreateGameResponse(response) {
		if (response.success) {
			facebook.sendRequests(locStrings["gameInviteTitle"], locStrings["gameInviteMessage"], {"gameId" : response.gameId});
			setTimeout(function() {
				viewManager.showView("gameList");
			}, 100);
		}
	}
};

AVOCADO.GameListMenuBuilder.getInstance = function(facebook, ajax, viewManager, templateRenderer, jqueryWrapper, locStrings) {
	return new AVOCADO.GameListMenuBuilder(facebook, ajax, viewManager, templateRenderer, jqueryWrapper, locStrings);
};
