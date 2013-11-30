if (AVOCADO == undefined) {
	AVOCADO = {};
}

AVOCADO.GameListElementBuilder = function(jqueryWrapper, templateRenderer, locStrings, playerNameDirectory, facebook) {
	this.buildListElement = function(gameData, clickHandler) {
		var templateParams = {
			"vs" : locStrings["vs"],
			"gameId" : gameData.gameId,
			"status" : locStrings[gameData.status]
		};
		var elementHtml = templateRenderer.renderTemplate("gameListEntry", templateParams);
		var element = jqueryWrapper.getElement(elementHtml);

		if ("waiting_for_more_players" == gameData.status) {
			element.addClass("tertiary");
		} else {
			element.find(".viewGameData").click(clickHandler);
			element.addClass("clickable");
			if (gameData.currentPlayerId == facebook.getSignedInPlayerId()) {
				element.addClass("primary");
			} else {
				element.addClass("secondary");
			}
		}

		var nameElement = element.find(".turn").find(".playerName");
		if (null == gameData.currentPlayerId) {
			nameElement.text(locStrings["n/a"]);
		} else {
			var namePromise = playerNameDirectory.getNamePromise(gameData.currentPlayerId);
			namePromise.registerForUpdates(nameElement);
		}

		var playerTable = element.find(".gameListElementTeams");
		for (var teamId = 0; teamId < 2; teamId++) {
			for (var index = 0; index < 2; index++) {
				var dataElement = playerTable.find(".playerNameContainer").has("input.team[value=" + teamId + "]").has("input.index[value=" + index + "]");
				var dataNameElement = dataElement.find(".playerName");
				if ((teamId in gameData.teams) && (index in gameData.teams[teamId])) {
					var namePromise = playerNameDirectory.getNamePromise(gameData.teams[teamId][index]);
					namePromise.registerForUpdates(dataNameElement);
				} else {
					dataNameElement.text(locStrings["inviteCTA"]);
					dataElement.addClass("clickable");
					dataElement.click(this.buildGameInviteClickHandler(gameData.gameId));
				}
			}
		}

		if (-1 != gameData.teams[0].indexOf(facebook.getSignedInPlayerId())) {
			element.find(".team0").addClass("green");
			element.find(".team1").addClass("red");
		} else {
			element.find(".team0").addClass("red");
			element.find(".team1").addClass("green");
		}

		return element;
	};

	this.buildGameInviteClickHandler = function(gameId) {
		return function(event) {
			facebook.sendRequests(locStrings["gameInviteTitle"], locStrings["gameInviteMessage"], {"gameId" : gameId});
		};
	};
};

AVOCADO.GameListElementBuilder.getInstance = function(jqueryWrapper, templateRenderer, locStrings, playerNameDirectory, facebook) {
	return new AVOCADO.GameListElementBuilder(jqueryWrapper, templateRenderer, locStrings, playerNameDirectory, facebook);
};