if (AVOCADO == undefined) {
	var AVOCADO = {};
}

AVOCADO.GameListMenuBuilder = function(facebook, ajax, viewManager, templateRenderer, jqueryWrapper, locStrings) {
	var self = this;

	this.buildGameMenu = function() {
		var element = jqueryWrapper.getElement(templateRenderer.renderTemplate("gameListMenu"));
		element.find(".createGameButton").click(self.createGameClickHandler);
		element.find(".inviteButton").click(self.appInviteClickHandler);
		element.find(".findGameButton").click(self.findGameClickHandler);
		element.find(".findGameStatus").hide();
		return element;
	};

	this.createGameClickHandler = function() {
		var params = {
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

	this.appInviteClickHandler = function() {
		facebook.sendRequests(locStrings["appInviteTitle"], locStrings["appInviteMessage"], {});
	};

	this.findGameClickHandler = function() {
		ajax.call("matchmake").done(handleFindGameResponse);
	};

	function handleFindGameResponse(response) {
		setTimeout(function() {
			viewManager.showView("gameList");
		}, 100);
	}
};

AVOCADO.GameListMenuBuilder.getInstance = function(facebook, ajax, viewManager, templateRenderer, jqueryWrapper, locStrings) {
	return new AVOCADO.GameListMenuBuilder(facebook, ajax, viewManager, templateRenderer, jqueryWrapper, locStrings);
};