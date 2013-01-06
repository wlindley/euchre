if (AVOCADO == undefined) {
	var AVOCADO = {};
}

AVOCADO.DiscardAreaBuilder = function(templateRenderer, jqueryWrapper, locStrings, ajax, playerId, viewManager) {
	var self = this;

	this.buildDiscardArea = function(status, cardElements, gameId, currentPlayerId) {
		if ("discard" != status) {
			return null;
		}

		if (currentPlayerId == playerId) {
			cardElements.addClass("clickableCard");
			cardElements.click(self.buildCardClickHandler(gameId));
		}

		var discardAreaHtml = templateRenderer.renderTemplate("discard", {"discardMessage" : locStrings.discardMessage});
		var discardElement = jqueryWrapper.getElement(discardAreaHtml);
		return discardElement;
	};

	this.buildCardClickHandler = function(gameId) {
		return function(event) {
			var target = jqueryWrapper.getElement(event.currentTarget);
			var suit = target.find(".cardSuit").val();
			var value = target.find(".cardValue").val();
			ajax.call("discard", {
				"playerId" : playerId,
				"gameId" : gameId,
				"suit" : suit,
				"value" : value
			}, self.buildRefreshViewFunc(gameId));
		};
	};

	this.buildRefreshViewFunc = function(gameId) {
		return function() {
			viewManager.showView("gamePlay", {"gameId" : gameId, "playerId" : playerId});
		};
	};
};

AVOCADO.DiscardAreaBuilder.getInstance = function(templateRenderer, jqueryWrapper, locStrings, ajax, playerId, viewManager) {
	return new AVOCADO.DiscardAreaBuilder(templateRenderer, jqueryWrapper, locStrings, ajax, playerId, viewManager);
};
