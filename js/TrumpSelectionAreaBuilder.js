if (AVOCADO == undefined) {
	var AVOCADO = {};
}

AVOCADO.TrumpSelectionAreaBuilder = function(templateRenderer) {
	var self = this;

	this.buildTrumpSelectionArea = function(upCard) {
		if (null == upCard) {
			return "";
		}
		var upCardHtml = templateRenderer.renderTemplate("card", {"suit" : upCard.suit, "value" : upCard.value});
		return templateRenderer.renderTemplate("trumpSelection", {"card" : upCardHtml});
	};
};

AVOCADO.TrumpSelectionAreaBuilder.getInstance = function(templateRenderer) {
	return new AVOCADO.TrumpSelectionAreaBuilder(templateRenderer);
};
