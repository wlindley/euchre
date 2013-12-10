if (AVOCADO == undefined) {
	var AVOCADO = {};
}

AVOCADO.TrumpSelectionAreaBuilder = function(templateRenderer, jqueryWrapper, ajax, facebook, locStrings, viewManager, playerNameDirectory) {
	var self = this;
	var SUITS = ["clubs", "diamonds", "spades", "hearts"];

	this.buildTrumpSelectionArea = function(upCard, status, gameId, dealerId, currentPlayerId, teams) {
		if ("trump_selection" != status && "trump_selection_2" != status) {
			return null;
		}

		var trumpSelectionActionHtml = "";
		if (facebook.getSignedInPlayerId() == currentPlayerId) {
			if ("trump_selection_2" == status) {
				trumpSelectionActionHtml = templateRenderer.renderTemplate("trumpSelection2Action", {});
			} else {
				trumpSelectionActionHtml = templateRenderer.renderTemplate("trumpSelection1Action", {});
			}
		}

		if (null == upCard) {
			upCard = {"suit" : 0, "value" : 0};
		}

		var dealerTeam = locStrings.yourTeam;
		if ((0 <= teams[0].indexOf(dealerId)) != (0 <= teams[0].indexOf(facebook.getSignedInPlayerId()))) {
			dealerTeam = locStrings.otherTeam;
		}

		var upCardHtml = templateRenderer.renderTemplate("card", {"suit" : upCard.suit, "value" : upCard.value});
		var trumpSelectionHtml = templateRenderer.renderTemplate("trumpSelection", {"card" : upCardHtml, "dealerTeam" : dealerTeam, "trumpSelectionAction" : trumpSelectionActionHtml});
		var trumpSelectionElement = jqueryWrapper.getElement(trumpSelectionHtml);
		if (facebook.getSignedInPlayerId() == currentPlayerId) {
			trumpSelectionElement.find(".trumpSelectionPassButton").click(self.buildPassClickHandler(gameId));
			trumpSelectionElement.find(".dealerPicksUpButton").click(self.buildDealerPicksUpClickHandler(gameId, upCard.suit));
			trumpSelectionElement.find(".selectTrumpSuitButton").click(self.buildSelectTrumpSuitClickHandler(gameId, trumpSelectionElement.find(".selectTrumpSuitInput")));
		} else {
			trumpSelectionElement.find(".trumpSelectionActions").hide();
		}

		var dealerNamePromise = playerNameDirectory.getNamePromise(dealerId);
		var dealerNameElement = trumpSelectionElement.find(".dealer").find(".playerName");
		dealerNamePromise.registerForUpdates(dealerNameElement);
		if ((-1 == teams[0].indexOf(facebook.getSignedInPlayerId())) == (-1 == teams[0].indexOf(dealerId))) {
			trumpSelectionElement.find(".dealer").find(".label").addClass("green");
		} else {
			trumpSelectionElement.find(".dealer").find(".label").addClass("red");
		}

		trumpSelectionElement.find(".ui.dropdown").dropdown();

		return trumpSelectionElement;
	};

	this.buildPassClickHandler = function(gameId) {
		return function(event) {
			ajax.call("selectTrump", {
				"suit" : 0,
				"playerId" : facebook.getSignedInPlayerId(),
				"gameId" : gameId
			}).done(self.buildRefreshViewFunc(gameId));
		};
	};

	this.buildDealerPicksUpClickHandler = function(gameId, upSuit) {
		return function(event) {
			ajax.call("selectTrump", {
				"suit" : upSuit,
				"playerId" : facebook.getSignedInPlayerId(),
				"gameId" : gameId
			}).done(self.buildRefreshViewFunc(gameId));
		};
	};

	this.buildSelectTrumpSuitClickHandler = function(gameId, inputElement) {
		return function(event) {
			var selectedSuit = inputElement.val().toLowerCase();
			var selectedSuitValue = SUITS.indexOf(selectedSuit) + 1; //offset since clubs = 1 on the server
			ajax.call("selectTrump", {
				"suit" : selectedSuitValue,
				"playerId" : facebook.getSignedInPlayerId(),
				"gameId" : gameId
			}).done(self.buildRefreshViewFunc(gameId));
		};
	};

	this.buildRefreshViewFunc = function(gameId) {
		return function(event) {
			setTimeout(function() {
				viewManager.showView("gamePlay", {"gameId" : gameId, "playerId" : facebook.getSignedInPlayerId()});
			}, 100);
		};
	};
};

AVOCADO.TrumpSelectionAreaBuilder.getInstance = function(templateRenderer, jqueryWrapper, ajax, facebook, locStrings, viewManager, playerNameDirectory) {
	return new AVOCADO.TrumpSelectionAreaBuilder(templateRenderer, jqueryWrapper, ajax, facebook, locStrings, viewManager, playerNameDirectory);
};
