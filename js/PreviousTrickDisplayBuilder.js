if (AVOCADO == undefined) {
	var AVOCADO = {};
}

AVOCADO.PreviousTrickDisplayBuilder = function(templateRenderer, jqueryWrapper, locStrings, playerId) {
	var self = this;

	this.buildPreviousTrickDisplay = function(playedCards, winnerId) {
		if (!isObjectValid(playedCards)) {
			return jqueryWrapper.getElement("<div />");
		}

		var cardHtmls = {};
		var index = 0;
		for (var pid in playedCards) {
			cardHtmls["card" + index] = templateRenderer.renderTemplate("card", playedCards[pid]);
			index++;
		}

		var element = jqueryWrapper.getElement(templateRenderer.renderTemplate("previousTrick", cardHtmls));

		wrapCard(element, playedCards[winnerId], "winningCard", templateRenderer.renderTemplate("winningCard"));
		wrapCard(element, playedCards[playerId], "playersCard", templateRenderer.renderTemplate("playersCard"));

		element.find("button.continue").click(this.buildContinueClickHandler(element));

		return element;
	};

	this.buildContinueClickHandler = function(rootElement) {
		return function(event) {
			rootElement.remove();
		};
	};

	function wrapCard(rootElement, targetCard, className, htmlText) {
		var target = rootElement.find("div.card").has("input.cardSuit[value=" + targetCard.suit + "]").has("input.cardValue[value=" + targetCard.value + "]");
		target.wrap("<div></div>");
		var targetParent = target.parent();
		targetParent.addClass(className);
		targetParent.append(htmlText);
	}

	function isObjectValid(obj) {
		if (undefined == obj) {
			return false;
		} else {
			for (var i in obj) {
				return true;
			}
			return false;
		}
		return true;
	}
};

AVOCADO.PreviousTrickDisplayBuilder.getInstance = function(templateRenderer, jqueryWrapper, locStrings, playerId) {
	return new AVOCADO.PreviousTrickDisplayBuilder(templateRenderer, jqueryWrapper, locStrings, playerId);
};