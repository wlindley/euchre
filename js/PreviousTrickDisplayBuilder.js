if (AVOCADO == undefined) {
	var AVOCADO = {};
}

AVOCADO.PreviousTrickDisplayBuilder = function(templateRenderer, jqueryWrapper, locStrings, playerId) {
	var self = this;

	this.buildPreviousTrickDisplay = function(playedCards, winnerId) {
		var cardHtmls = {};
		var index = 0;
		for (var pid in playedCards) {
			cardHtmls["card" + index] = templateRenderer.renderTemplate("card", playedCards[pid]);
			index++;
		}

		var element = jqueryWrapper.getElement(templateRenderer.renderTemplate("previousTrick", cardHtmls));

		addClassToCard(element, playedCards[playerId], "playersCard");
		addClassToCard(element, playedCards[winnerId], "winningCard");

		element.find("button.continue").click(this.buildContinueClickHandler(element));

		return element;
	};

	this.buildContinueClickHandler = function(rootElement) {
		return function(event) {
			rootElement.remove();
		};
	};

	function addClassToCard(rootElement, targetCard, className) {
		rootElement.find("div.card").has("input.cardSuit[value=" + targetCard.suit + "]").has("input.cardValue[value=" + targetCard.value + "]").addClass(className);
	}
};

AVOCADO.PreviousTrickDisplayBuilder.getInstance = function(templateRenderer, jqueryWrapper, locStrings, playerId) {
	return new AVOCADO.PreviousTrickDisplayBuilder(templateRenderer, jqueryWrapper, locStrings, playerId);
};