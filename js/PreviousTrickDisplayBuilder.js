if (AVOCADO == undefined) {
	var AVOCADO = {};
}

AVOCADO.PreviousTrickDisplayBuilder = function(templateRenderer, jqueryWrapper, locStrings, playerId) {
	var self = this;

	this.buildPreviousTrickDisplay = function(playedCards, winnerId) {
		if (!isObjectValid(playedCards)) {
			return jqueryWrapper.getElement("<div />");
		}

		var trickElementHtmls = {};
		var index = 0;
		for (var pid in playedCards) {
			var cardHtml = templateRenderer.renderTemplate("card", playedCards[pid]);
			var playerName = locStrings["player"].replace("%playerId%", pid);
			trickElementHtmls["card" + index] = templateRenderer.renderTemplate("trickElement", {"player" : playerName, "card" : cardHtml});
			index++;
		}

		var element = jqueryWrapper.getElement(templateRenderer.renderTemplate("previousTrick", trickElementHtmls));

		updateElement(element, playedCards[winnerId], "winningCard", templateRenderer.renderTemplate("winningCard"));
		updateElement(element, playedCards[playerId], "playersCard", templateRenderer.renderTemplate("playersCard"));

		element.find("button.continue").click(this.buildContinueClickHandler(element));

		return element;
	};

	this.buildContinueClickHandler = function(rootElement) {
		var self = this;
		return function(event) {
			rootElement.hide(100, self.buildHideCompleteHandler(rootElement));
		};
	};

	this.buildHideCompleteHandler = function(rootElement) {
		return function(event) {
			rootElement.remove();
		};
	};

	function updateElement(rootElement, targetCard, className, htmlText) {
		var target = rootElement.find("div.trickElement").has("input.cardSuit[value=" + targetCard.suit + "]").has("input.cardValue[value=" + targetCard.value + "]");
		target.addClass(className);
		target.append(htmlText);
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