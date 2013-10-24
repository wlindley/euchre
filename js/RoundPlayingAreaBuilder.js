if (AVOCADO == undefined) {
	var AVOCADO = {};
}

AVOCADO.RoundPlayingAreaBuilder = function(templateRenderer, jqueryWrapper, locStrings, ajax, playerId, viewManager, playerNameDirectory) {
	var self = this;

	this.buildRoundPlayingArea = function(status, ledSuit, trick, cardElements, gameId, currentPlayerId, leaderId, teams) {
		if ("round_in_progress" != status) {
			return null;
		}

		if (currentPlayerId == playerId) {
			cardElements.addClass("clickableCard");
			cardElements.click(self.buildCardClickHandler(gameId));
		}

		var ledSuitString = locStrings["suit_" + ledSuit];
		if (0 == ledSuit) {
			ledSuitString = locStrings["noCardsPlayed"];
		}

		var leaderHtml = "";
		if (null != leaderId) {
			//var leaderName = locStrings["player"].replace("%playerId%", leaderId);
			var teamString = locStrings.yourTeam;
			if ((0 <= (teams[0].indexOf(playerId))) != (0 <= (teams[0].indexOf(leaderId)))) {
				teamString = locStrings.otherTeam;
			}
			leaderHtml = templateRenderer.renderTemplate("leader", {"team" : teamString});
		}

		var trickHtml = "";
		for (var pid in trick) {
			var cardHtml = templateRenderer.renderTemplate("card", {"suit" : trick[pid].suit, value : trick[pid].value});
			trickHtml += templateRenderer.renderTemplate("trickElement", {"card" : cardHtml});
		}

		var roundPlayingAreaHtml = templateRenderer.renderTemplate("playingRound", {"ledSuit" : ledSuitString, "currentTrick" : trickHtml, "leader" : leaderHtml});
		var roundPlayingElement = jqueryWrapper.getElement(roundPlayingAreaHtml);

		for (var pid in trick) {
			var card = trick[pid];
			var trickElement = roundPlayingElement.find(".trickElement").has("input.cardSuit[value=" + card.suit + "]").has("input.cardValue[value=" + card.value + "]");
			var nameElement = trickElement.find(".playerName");
			var namePromise = playerNameDirectory.getNamePromise(pid);
			namePromise.registerForUpdates(nameElement);
		}

		return roundPlayingElement;
	};

	this.buildCardClickHandler = function(gameId) {
		return function(event) {
			var target = jqueryWrapper.getElement(event.currentTarget);
			var suit = target.find(".cardSuit").val();
			var value = target.find(".cardValue").val();
			ajax.call("playCard", {
				"playerId" : playerId,
				"gameId" : gameId,
				"suit" : suit,
				"value" : value
			}, self.buildRefreshViewFunc(gameId));
		};
	};

	this.buildRefreshViewFunc = function(gameId) {
		return function() {
			setTimeout(function() {
				viewManager.showView("gamePlay", {"gameId" : gameId, "playerId" : playerId});
			}, 100);
		};
	};
};

AVOCADO.RoundPlayingAreaBuilder.getInstance = function(templateRenderer, jqueryWrapper, locStrings, ajax, playerId, viewManager, playerNameDirectory) {
	return new AVOCADO.RoundPlayingAreaBuilder(templateRenderer, jqueryWrapper, locStrings, ajax, playerId, viewManager, playerNameDirectory);
};
