if (AVOCADO == undefined) {
	var AVOCADO = {};
}

AVOCADO.TrumpSelectionAreaBuilder = function(templateRenderer, jqueryWrapper, ajax, playerId, locStrings, viewManager) {
	var self = this;
	var SUITS = ["clubs", "diamonds", "spades", "hearts"];

	this.buildTrumpSelectionArea = function(upCard, status, gameId, dealerId, currentPlayerId) {
		if ("round_in_progress" == status) {
			return null;
		}
		var trumpSelectionActionHtml = "";
		if (playerId == currentPlayerId) {
			if ("trump_selection_2" == status) {
				trumpSelectionActionHtml = templateRenderer.renderTemplate("trumpSelection2Action", {});
				upCard = {"suit" : 0, "value" : 0};
			} else {
				trumpSelectionActionHtml = templateRenderer.renderTemplate("trumpSelection1Action", {});
			}
		}
		var dealerName = locStrings.player.replace("%playerId%", dealerId);
		var upCardHtml = templateRenderer.renderTemplate("card", {"suit" : upCard.suit, "value" : upCard.value});
		var trumpSelectionHtml = templateRenderer.renderTemplate("trumpSelection", {"card" : upCardHtml, "dealerName" : dealerName, "trumpSelectionAction" : trumpSelectionActionHtml});
		var trumpSelectionElement = jqueryWrapper.getElement(trumpSelectionHtml);
		if (playerId == currentPlayerId) {
			trumpSelectionElement.find(".trumpSelectionPassButton").click(self.buildPassClickHandler(gameId));
			trumpSelectionElement.find(".dealerPicksUpButton").click(self.buildDealerPicksUpClickHandler(gameId, upCard.suit));
			trumpSelectionElement.find(".selectTrumpSuitButton").click(self.buildSelectTrumpSuitClickHandler(gameId, trumpSelectionElement.find(".selectTrumpSuitInput")));
		} else {
			trumpSelectionElement.find(".trumpSelectionPassButton").hide();
		}
		return trumpSelectionElement;
	};

	this.buildPassClickHandler = function(gameId) {
		return function(event) {
			ajax.call("selectTrump", {
				"suit" : 0,
				"playerId" : playerId,
				"gameId" : gameId
			}, self.buildRefreshViewFunc(gameId));
		};
	};

	this.buildDealerPicksUpClickHandler = function(gameId, upSuit) {
		return function(event) {
			ajax.call("selectTrump", {
				"suit" : upSuit,
				"playerId" : playerId,
				"gameId" : gameId
			}, self.buildRefreshViewFunc(gameId));
		};
	};

	this.buildSelectTrumpSuitClickHandler = function(gameId, inputElement) {
		return function(event) {
			var selectedSuit = inputElement.val().toLowerCase();
			var selectedSuitValue = SUITS.indexOf(selectedSuit) + 1; //offset since clubs = 1 on the server
			ajax.call("selectTrump", {
				"suit" : selectedSuitValue,
				"playerId" : playerId,
				"gameId" : gameId
			}, self.buildRefreshViewFunc(gameId));
		};
	};

	this.buildRefreshViewFunc = function(gameId) {
		return function(event) {
			viewManager.showView("gamePlay", {"gameId" : gameId, "playerId" : playerId});
		};
	};
};

AVOCADO.TrumpSelectionAreaBuilder.getInstance = function(templateRenderer, jqueryWrapper, ajax, playerId, locStrings, viewManager) {
	return new AVOCADO.TrumpSelectionAreaBuilder(templateRenderer, jqueryWrapper, ajax, playerId, locStrings, viewManager);
};
