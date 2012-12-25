if (AVOCADO == undefined) {
	var AVOCADO = {};
}

AVOCADO.TrumpSelectionAreaBuilder = function(templateRenderer, jqueryWrapper, ajax, playerId) {
	var self = this;

	this.buildTrumpSelectionArea = function(upCard, status, gameId) {
		if (null == upCard || "round_in_progress" == status) {
			return null;
		}
		var upCardHtml = templateRenderer.renderTemplate("card", {"suit" : upCard.suit, "value" : upCard.value});
		var trumpSelectionHtml = templateRenderer.renderTemplate("trumpSelection", {"card" : upCardHtml});
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

AVOCADO.TrumpSelectionAreaBuilder.getInstance = function(templateRenderer, jqueryWrapper, ajax, playerId) {
	return new AVOCADO.TrumpSelectionAreaBuilder(templateRenderer, jqueryWrapper, ajax, playerId);
};
