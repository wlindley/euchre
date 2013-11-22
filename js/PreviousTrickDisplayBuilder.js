if (AVOCADO == undefined) {
	var AVOCADO = {};
}

AVOCADO.PreviousTrickDisplayBuilder = function(templateRenderer, jqueryWrapper, playerNameDirectory) {
	var self = this;

	this.buildPreviousTrickDisplay = function(playedCards, winnerId) {
		if (!isObjectValid(playedCards)) {
			return jqueryWrapper.getElement("<div />");
		}

		var trickElementHtmls = {};
		var index = 0;
		for (var pid in playedCards) {
			var cardHtml = templateRenderer.renderTemplate("card", playedCards[pid]);
			trickElementHtmls["card" + index] = templateRenderer.renderTemplate("trickElement", {"card" : cardHtml});
			index++;
		}

		var element = jqueryWrapper.getElement(templateRenderer.renderTemplate("previousTrick", trickElementHtmls));

		for (pid in playedCards) {
			var trickElementElement = getTrickElementByCard(element, playedCards[pid]);
			var namePromise = playerNameDirectory.getNamePromise(pid);
			namePromise.registerForUpdates(trickElementElement.find(".playerName"));
		}

		updateElement(element, playedCards[winnerId], "winningCard", templateRenderer.renderTemplate("winningCard"));

		element.find("button.continue").click(this.buildContinueClickHandler(element));

		return element;
	};

	this.buildContinueClickHandler = function(rootElement) {
		var self = this;
		return function(event) {
			rootElement.parent().fadeOut(100, self.buildHideCompleteHandler(rootElement));
		};
	};

	this.buildHideCompleteHandler = function(rootElement) {
		return function(event) {
			rootElement.parent().remove();
		};
	};

	function getTrickElementByCard(rootElement, targetCard) {
		return rootElement.find("div.trickElement").has("input.cardSuit[value=" + targetCard.suit + "]").has("input.cardValue[value=" + targetCard.value + "]");
	}

	function updateElement(rootElement, targetCard, className, htmlText) {
		var target = getTrickElementByCard(rootElement, targetCard);
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

AVOCADO.PreviousTrickDisplayBuilder.getInstance = function(templateRenderer, jqueryWrapper, playerNameDirectory) {
	return new AVOCADO.PreviousTrickDisplayBuilder(templateRenderer, jqueryWrapper, playerNameDirectory);
};