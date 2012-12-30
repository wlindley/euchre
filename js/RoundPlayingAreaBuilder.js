if (AVOCADO == undefined) {
	var AVOCADO = {};
}

AVOCADO.RoundPlayingAreaBuilder = function(templateRenderer, jqueryWrapper, locStrings) {
	var self = this;

	this.buildRoundPlayingArea = function(status, ledSuit, trick) {
		if ("round_in_progress" != status) {
			return null;
		}

		var ledSuitString = locStrings["suit_" + ledSuit];

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
};

AVOCADO.RoundPlayingAreaBuilder.getInstance = function(templateRenderer, jqueryWrapper, locStrings) {
	return new AVOCADO.RoundPlayingAreaBuilder(templateRenderer, jqueryWrapper, locStrings);
};
