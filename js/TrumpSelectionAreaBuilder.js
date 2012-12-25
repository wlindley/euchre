if (AVOCADO == undefined) {
	var AVOCADO = {};
}

AVOCADO.TrumpSelectionAreaBuilder = function(templateRenderer, jqueryWrapper) {
	var self = this;

	this.buildTrumpSelectionArea = function(upCard, status) {
		if (null == upCard || "round_in_progress" == status) {
			return null;
		}
		var upCardHtml = templateRenderer.renderTemplate("card", {"suit" : upCard.suit, "value" : upCard.value});
		var trumpSelectionHtml = templateRenderer.renderTemplate("trumpSelection", {"card" : upCardHtml});
		var trumpSelectionElement = jqueryWrapper.getElement(trumpSelectionHtml);
		trumpSelectionElement.find(".trumpSelectionPassButton").click(self.handlePassClicked);
		return trumpSelectionElement;
	};

	this.handlePassClicked = function(event) {
		
	};
};

AVOCADO.TrumpSelectionAreaBuilder.getInstance = function(templateRenderer, jqueryWrapper) {
	return new AVOCADO.TrumpSelectionAreaBuilder(templateRenderer, jqueryWrapper);
};
