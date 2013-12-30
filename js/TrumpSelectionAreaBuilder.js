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

		if (null == upCard) {
			upCard = {"suit" : 0, "value" : 0};
		}

		var trumpSelectionElement = buildTrumpSelectionElement(teams, status, dealerId, currentPlayerId, upCard);
		setupActions(trumpSelectionElement, gameId, currentPlayerId, upCard);
		showDealerNameAndTeam(trumpSelectionElement, teams, dealerId);

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

	function buildTrumpSelectionAction(status, currentPlayerId) {
		if (facebook.getSignedInPlayerId() == currentPlayerId) {
			if ("trump_selection_2" == status) {
				return templateRenderer.renderTemplate("trumpSelection2Action");
			} else {
				return templateRenderer.renderTemplate("trumpSelection1Action");
			}
		}
		return "";
	}

	function buildDealerTeam(teams, dealerId) {
		if ((0 <= teams[0].indexOf(dealerId)) != (0 <= teams[0].indexOf(facebook.getSignedInPlayerId()))) {
			return locStrings.otherTeam;
		}
		return locStrings.yourTeam;
	}

	function buildTrumpSelectionElement(teams, status, dealerId, currentPlayerId, upCard) {
		var trumpSelectionActionHtml = buildTrumpSelectionAction(status, currentPlayerId);
		var dealerTeam = buildDealerTeam(teams, dealerId);
		var upCardHtml = templateRenderer.renderTemplate("card", {"suit" : upCard.suit, "value" : upCard.value});
		
		var trumpSelectionHtml = templateRenderer.renderTemplate("trumpSelection", {"card" : upCardHtml, "dealerTeam" : dealerTeam, "trumpSelectionAction" : trumpSelectionActionHtml});
		return jqueryWrapper.getElement(trumpSelectionHtml);
	}

	function setupActions(trumpSelectionElement, gameId, currentPlayerId, upCard) {
		if (facebook.getSignedInPlayerId() == currentPlayerId) {
			trumpSelectionElement.find(".trumpSelectionPassButton").click(self.buildPassClickHandler(gameId));
			trumpSelectionElement.find(".dealerPicksUpButton").click(self.buildDealerPicksUpClickHandler(gameId, upCard.suit));
			trumpSelectionElement.find(".selectTrumpSuitButton").click(self.buildSelectTrumpSuitClickHandler(gameId, trumpSelectionElement.find(".selectTrumpSuitInput")));
		} else {
			trumpSelectionElement.find(".trumpSelectionActions").hide();
		}
	}

	function showDealerNameAndTeam(trumpSelectionElement, teams, dealerId) {
		var dealerNamePromise = playerNameDirectory.getNamePromise(dealerId);
		var dealerNameElement = trumpSelectionElement.find(".dealer").find(".playerName");
		dealerNamePromise.registerForUpdates(dealerNameElement);
		if ((-1 == teams[0].indexOf(facebook.getSignedInPlayerId())) == (-1 == teams[0].indexOf(dealerId))) {
			trumpSelectionElement.find(".dealer").find(".label").addClass("green");
		} else {
			trumpSelectionElement.find(".dealer").find(".label").addClass("red");
		}
	}
};

AVOCADO.TrumpSelectionAreaBuilder.getInstance = function(templateRenderer, jqueryWrapper, ajax, facebook, locStrings, viewManager, playerNameDirectory) {
	return new AVOCADO.TrumpSelectionAreaBuilder(templateRenderer, jqueryWrapper, ajax, facebook, locStrings, viewManager, playerNameDirectory);
};
