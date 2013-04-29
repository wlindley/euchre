if (AVOCADO == undefined) {
	var AVOCADO = {};
}

AVOCADO.PreviousTrickDisplayBuilder = function(templateRenderer, jqueryWrapper, locStrings, playerId) {
	var self = this;

	this.buildPreviousTrickDisplay = function(playedCards, winnerId) {
		throw new Exception("Not Yet Implemented");
	};
};

AVOCADO.PreviousTrickDisplayBuilder.getInstance = function(templateRenderer, jqueryWrapper, locStrings, playerId) {
	return new AVOCADO.PreviousTrickDisplayBuilder(templateRenderer, jqueryWrapper, locStrings, playerId);
};