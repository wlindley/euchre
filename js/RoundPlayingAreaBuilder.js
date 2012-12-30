if (AVOCADO == undefined) {
	var AVOCADO = {};
}

AVOCADO.RoundPlayingAreaBuilder = function(templateRenderer, jqueryWrapper, locStrings, ajax, playerId, viewManager) {
	var self = this;

	this.buildRoundPlayingArea = function(status, ledSuit, trick, cardElements, gameId) {
		if ("round_in_progress" != status) {
			return null;
		}

		cardElements.addClass("clickableCard");
		cardElements.click(self.buildCardClickHandler(gameId));

		var ledSuitString = locStrings["suit_" + ledSuit];
		if (0 == ledSuit) {
			ledSuitString = locStrings["noCardsPlayed"];
		}

		var trickHtml = "";
		for (var playerId in trick) {
			var playerName = locStrings["player"].replace("%playerId%", playerId);
			var cardHtml = templateRenderer.renderTemplate("card", {"suit" : trick[playerId].suit, value : trick[playerId].value});
			trickHtml += templateRenderer.renderTemplate("trickElement", {"player" : playerName, "card" : cardHtml});
		}

		var roundPlayingAreaHtml = templateRenderer.renderTemplate("playingRound", {"ledSuit" : ledSuitString, "currentTrick" : trickHtml});
		var roundPlayingElement = jqueryWrapper.getElement(roundPlayingAreaHtml);
		return roundPlayingElement;
	};

	this.buildCardClickHandler = function(gameId) {
		return function(event) {
			var target = jqueryWrapper.getElement(event.currentTarget);
			var suit = target.find(".cardSuit").val();
			var value = target.find(".cardValue").val();
			ajax.call("playCard", {
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

AVOCADO.RoundPlayingAreaBuilder.getInstance = function(templateRenderer, jqueryWrapper, locStrings, ajax, playerId, viewManager) {
	return new AVOCADO.RoundPlayingAreaBuilder(templateRenderer, jqueryWrapper, locStrings, ajax, playerId, viewManager);
};
