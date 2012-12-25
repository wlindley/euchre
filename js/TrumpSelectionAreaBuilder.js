if (AVOCADO == undefined) {
	var AVOCADO = {};
}

AVOCADO.TrumpSelectionAreaBuilder = function(templateRenderer, jqueryWrapper, ajax, playerId, locStrings) {
	var self = this;

	this.buildTrumpSelectionArea = function(upCard, status, gameId, dealerId) {
		if (null == upCard || "round_in_progress" == status) {
			return null;
		}
		var dealerName = locStrings.player.replace("%playerId%", dealerId);
		var upCardHtml = templateRenderer.renderTemplate("card", {"suit" : upCard.suit, "value" : upCard.value});
		var trumpSelectionHtml = templateRenderer.renderTemplate("trumpSelection", {"card" : upCardHtml, "dealerName" : dealerName});
		var trumpSelectionElement = jqueryWrapper.getElement(trumpSelectionHtml);
		trumpSelectionElement.find(".trumpSelectionPassButton").click(self.buildPassClickHandler(gameId));
		return trumpSelectionElement;
	};

	this.buildPassClickHandler = function(gameId) {
		return function(event) {
			ajax.call("selectTrump", {
				"suit" : null,
				"playerId" : playerId,
				"gameId" : gameId
			}, function() {});
		};
	};
};

AVOCADO.TrumpSelectionAreaBuilder.getInstance = function(templateRenderer, jqueryWrapper, ajax, playerId, locStrings) {
	return new AVOCADO.TrumpSelectionAreaBuilder(templateRenderer, jqueryWrapper, ajax, playerId, locStrings);
};
