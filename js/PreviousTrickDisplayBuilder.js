if (AVOCADO == undefined) {
	var AVOCADO = {};
}

AVOCADO.PreviousTrickDisplayBuilder = function(templateRenderer, jqueryWrapper, playerNameDirectory, facebook, teamUtils) {
	var self = this;

	this.buildPreviousTrickDisplay = function(playedCards, winnerId, teams) {
		if (!AVOCADO.isObjectEmpty(playedCards)) {
			return jqueryWrapper.getElement(templateRenderer.renderTemplate("emptyDiv"));
		}

		var element = buildElement(playedCards);
		hookUpNamePromisesAndSetTeamColors(element, playedCards, teams);
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

	function buildElement(playedCards) {
		var trickElementHtmls = {};
		var index = 0;
		for (var pid in playedCards) {
			var cardHtml = templateRenderer.renderTemplate("card", playedCards[pid]);
			trickElementHtmls["card" + index] = templateRenderer.renderTemplate("trickElement", {"card" : cardHtml});
			index++;
		}

		return jqueryWrapper.getElement(templateRenderer.renderTemplate("previousTrick", trickElementHtmls));
	}

	function hookUpNamePromisesAndSetTeamColors(element, playedCards, teams) {
		var localPlayerId = facebook.getSignedInPlayerId();
		for (pid in playedCards) {
			var trickElementElement = getTrickElementByCard(element, playedCards[pid]);
			var trickElementNameElement = trickElementElement.find(".playerName");
			trickElementNameElement.addClass(teamUtils.getClassForPlayer(teams, pid));

			var namePromise = playerNameDirectory.getNamePromise(pid);
			namePromise.registerForUpdates(trickElementNameElement);
		}
	}
};

AVOCADO.PreviousTrickDisplayBuilder.getInstance = function(templateRenderer, jqueryWrapper, playerNameDirectory, facebook, teamUtils) {
	return new AVOCADO.PreviousTrickDisplayBuilder(templateRenderer, jqueryWrapper, playerNameDirectory, facebook, teamUtils);
};