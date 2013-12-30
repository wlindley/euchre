if (AVOCADO == undefined) {
	var AVOCADO = {};
}

AVOCADO.RoundPlayingAreaBuilder = function(templateRenderer, jqueryWrapper, locStrings, ajax, facebook, viewManager, playerNameDirectory) {
	var self = this;

	this.buildRoundPlayingArea = function(status, ledSuit, trick, cardElements, gameId, currentPlayerId, leaderId, teams) {
		if ("round_in_progress" != status) {
			return null;
		}

		makeCardsClickable(cardElements, currentPlayerId, gameId);

		var roundPlayingElement = buildRoundPlayingElement(teams, trick, leaderId, ledSuit);
		hookUpNamePromisesAndSetTeamColors(roundPlayingElement, teams, trick);
		showLeaderName(roundPlayingElement, leaderId);

		return roundPlayingElement;
	};

	this.buildCardClickHandler = function(gameId) {
		return function(event) {
			var target = jqueryWrapper.getElement(event.currentTarget);
			var suit = target.find(".cardSuit").val();
			var value = target.find(".cardValue").val();
			ajax.call("playCard", {
				"playerId" : facebook.getSignedInPlayerId(),
				"gameId" : gameId,
				"suit" : suit,
				"value" : value
			}).done(self.buildRefreshViewFunc(gameId));
		};
	};

	this.buildRefreshViewFunc = function(gameId) {
		return function() {
			setTimeout(function() {
				viewManager.showView("gamePlay", {"gameId" : gameId, "playerId" : facebook.getSignedInPlayerId()});
			}, 100);
		};
	};

	function makeCardsClickable(cardElements, currentPlayerId, gameId) {
		if (currentPlayerId == facebook.getSignedInPlayerId()) {
			cardElements.addClass("clickable");
			cardElements.click(self.buildCardClickHandler(gameId));
		}
	}

	function buildLetSuitString(ledSuit) {
		var ledSuitString = locStrings["suit_" + ledSuit];
		if (0 == ledSuit) {
			ledSuitString = locStrings["noCardsPlayed"];
		}
		return ledSuitString;
	}

	function buildLeaderHtml(leaderId, teams) {
		if (null != leaderId) {
			var teamString = locStrings.yourTeam;
			if ((0 <= (teams[0].indexOf(facebook.getSignedInPlayerId()))) != (0 <= (teams[0].indexOf(leaderId)))) {
				teamString = locStrings.otherTeam;
			}
			return templateRenderer.renderTemplate("leader", {"team" : teamString});
		}
		return "";
	}

	function buildTrickHtml(trick) {
		var trickHtml = "";
		for (var pid in trick) {
			var cardHtml = templateRenderer.renderTemplate("card", {"suit" : trick[pid].suit, value : trick[pid].value});
			trickHtml += templateRenderer.renderTemplate("trickElement", {"card" : cardHtml});
		}
		return trickHtml;
	}

	function buildRoundPlayingElement(teams, trick, leaderId, ledSuit) {
		var ledSuitString = buildLetSuitString(ledSuit);
		var leaderHtml = buildLeaderHtml(leaderId, teams);
		var trickHtml = buildTrickHtml(trick);

		var roundPlayingAreaHtml = templateRenderer.renderTemplate("playingRound", {"ledSuit" : ledSuitString, "currentTrick" : trickHtml, "leader" : leaderHtml});
		return jqueryWrapper.getElement(roundPlayingAreaHtml);
	}

	function hookUpNamePromisesAndSetTeamColors(roundPlayingElement, teams, trick) {
		var localPlayerId = facebook.getSignedInPlayerId();
		for (var pid in trick) {
			var card = trick[pid];
			var trickElement = roundPlayingElement.find(".trickElement").has("input.cardSuit[value=" + card.suit + "]").has("input.cardValue[value=" + card.value + "]");
			var nameElement = trickElement.find(".playerName");
			var namePromise = playerNameDirectory.getNamePromise(pid);
			namePromise.registerForUpdates(nameElement);
			var color = "green";
			if ((0 <= (teams[0].indexOf(localPlayerId))) != (0 <= (teams[0].indexOf(pid)))) {
				color = "red";
			}
			nameElement.addClass(color);
		}
	}

	function showLeaderName(roundPlayingElement, leaderId) {
		if (null != leaderId) {
			var leaderElement = roundPlayingElement.find(".leader");
			var leaderNameElement = leaderElement.find(".playerName");
			var leaderNamePromise = playerNameDirectory.getNamePromise(leaderId);
			leaderNamePromise.registerForUpdates(leaderNameElement);
		}
	}
};

AVOCADO.RoundPlayingAreaBuilder.getInstance = function(templateRenderer, jqueryWrapper, locStrings, ajax, facebook, viewManager, playerNameDirectory) {
	return new AVOCADO.RoundPlayingAreaBuilder(templateRenderer, jqueryWrapper, locStrings, ajax, facebook, viewManager, playerNameDirectory);
};
