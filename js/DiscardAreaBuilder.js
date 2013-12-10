if (AVOCADO == undefined) {
	var AVOCADO = {};
}

AVOCADO.DiscardAreaBuilder = function(templateRenderer, jqueryWrapper, locStrings, ajax, facebook, viewManager) {
	var self = this;

	this.buildDiscardArea = function(status, cardElements, gameId, currentPlayerId) {
		if ("discard" != status || currentPlayerId != facebook.getSignedInPlayerId()) {
			return null;
		}

		cardElements.addClass("clickable");
		cardElements.click(self.buildCardClickHandler(gameId));

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
				"playerId" : facebook.getSignedInPlayerId(),
				"gameId" : gameId,
				"suit" : suit,
				"value" : value
			}).done(self.buildRefreshViewFunc(gameId));
		};
	};

	this.buildRefreshViewFunc = function(gameId) {
		return function() {
			setTimeout(function() {
				viewManager.showView("gamePlay", {"gameId" : gameId, "playerId" : facebook.getSignedInPlayerId()});
			}, 100);
		};
	};
};

AVOCADO.DiscardAreaBuilder.getInstance = function(templateRenderer, jqueryWrapper, locStrings, ajax, facebook, viewManager) {
	return new AVOCADO.DiscardAreaBuilder(templateRenderer, jqueryWrapper, locStrings, ajax, facebook, viewManager);
};
