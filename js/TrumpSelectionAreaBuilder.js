if (AVOCADO == undefined) {
	var AVOCADO = {};
}

AVOCADO.TrumpSelectionAreaBuilder = function(templateRenderer, jqueryWrapper, ajax, facebook, locStrings, viewManager, playerNameDirectory, teamUtils) {
	var self = this;
	var SUITS = ["clubs", "diamonds", "spades", "hearts"];

	this.buildTrumpSelectionArea = function(upCard, status, gameId, dealerId, currentPlayerId, teams, blackListedSuits) {
		if ("trump_selection" != status && "trump_selection_2" != status) {
			return null;
		}

		if (null == upCard) {
			upCard = {"suit" : 0, "value" : 0};
		}

		var trumpSelectionElement = buildTrumpSelectionElement(teams, status, dealerId, currentPlayerId, upCard, blackListedSuits);
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

	function buildTrumpSelectionAction(status, currentPlayerId, blackListedSuits) {
		if (facebook.getSignedInPlayerId() == currentPlayerId) {
			if ("trump_selection_2" == status) {
				return buildTrumpSelection2Action(blackListedSuits);
			} else {
				return templateRenderer.renderTemplate("trumpSelection1Action");
			}
		}
		return "";
	}

	function buildTrumpSelection2Action(blackListedSuits) {
		var suits = [1, 2, 3, 4];
		for (var i in blackListedSuits) {
			suits.splice(suits.indexOf(blackListedSuits[i]), 1);
		}
		var activeTrumpId = "";
		var activeTrumpName = "";
		var trumpItemsHtml = "";
		for (var i in suits) {
			var trumpId = locStrings["suit_" + suits[i]];
			var trumpName = locStrings["suit_" + suits[i] + "_cap"];
			if (0 == i) {
				trumpItemsHtml += templateRenderer.renderTemplate("trumpSelection2ItemActive", {"trumpId" : trumpId, "trumpName" : trumpName});
				activeTrumpId = trumpId;
				activeTrumpName = trumpName;
			} else {
				trumpItemsHtml += templateRenderer.renderTemplate("trumpSelection2Item", {"trumpId" : trumpId, "trumpName" : trumpName});
			}
		}
		return templateRenderer.renderTemplate("trumpSelection2Action", {"activeTrumpId" : activeTrumpId, "activeTrumpName" : activeTrumpName, "trumpSelectionItems" : trumpItemsHtml});
	}

	function buildDealerTeam(teams, dealerId) {
		if (!teamUtils.isOnLocalPlayersTeam(teams, dealerId)) {
			return locStrings.otherTeam;
		}
		return locStrings.yourTeam;
	}

	function buildTrumpSelectionElement(teams, status, dealerId, currentPlayerId, upCard, blackListedSuits) {
		var trumpSelectionActionHtml = buildTrumpSelectionAction(status, currentPlayerId, blackListedSuits);
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
		var dealerNameLabel = trumpSelectionElement.find(".dealer").find(".label");
		dealerNameLabel.addClass(teamUtils.getClassForPlayer(teams, dealerId));
	}
};

AVOCADO.TrumpSelectionAreaBuilder.getInstance = function(templateRenderer, jqueryWrapper, ajax, facebook, locStrings, viewManager, playerNameDirectory, teamUtils) {
	return new AVOCADO.TrumpSelectionAreaBuilder(templateRenderer, jqueryWrapper, ajax, facebook, locStrings, viewManager, playerNameDirectory, teamUtils);
};
