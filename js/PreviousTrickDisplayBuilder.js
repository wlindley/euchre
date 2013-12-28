if (AVOCADO == undefined) {
	var AVOCADO = {};
}

AVOCADO.PreviousTrickDisplayBuilder = function(templateRenderer, jqueryWrapper, playerNameDirectory, facebook) {
	var self = this;

	this.buildPreviousTrickDisplay = function(playedCards, winnerId, teams) {
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

		var localPlayerId = facebook.getSignedInPlayerId();
		for (pid in playedCards) {
			var trickElementElement = getTrickElementByCard(element, playedCards[pid]);
			var trickElementNameElement = trickElementElement.find(".playerName");
			var color = "green";
			if ((-1 == teams[0].indexOf(localPlayerId)) != (-1 == teams[0].indexOf(pid))) {
				color = "red";
			}
			trickElementNameElement.addClass(color);

			var namePromise = playerNameDirectory.getNamePromise(pid);
			namePromise.registerForUpdates(trickElementNameElement);
		}

		setWinningCard(element, playedCards[winnerId]);

		element.find(".continueButton").click(this.buildContinueClickHandler(element));

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
			console.log("removing");
			console.log(rootElement.parent());
			rootElement.parent().remove();
		};
	};

	function getTrickElementByCard(rootElement, targetCard) {
		return rootElement.find("div.trickElement").has("input.cardSuit[value=" + targetCard.suit + "]").has("input.cardValue[value=" + targetCard.value + "]");
	}

	function setWinningCard(rootElement, targetCard) {
		var target = getTrickElementByCard(rootElement, targetCard);
		target.find(".card").append(templateRenderer.renderTemplate("winnerLabel"));
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

AVOCADO.PreviousTrickDisplayBuilder.getInstance = function(templateRenderer, jqueryWrapper, playerNameDirectory, facebook) {
	return new AVOCADO.PreviousTrickDisplayBuilder(templateRenderer, jqueryWrapper, playerNameDirectory, facebook);
};