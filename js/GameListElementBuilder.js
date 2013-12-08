if (AVOCADO == undefined) {
	AVOCADO = {};
}

AVOCADO.GameListElementBuilder = function(jqueryWrapper, templateRenderer, locStrings, playerNameDirectory, facebook, ajax, viewManager) {
	var self = this;

	this.buildListElement = function(gameData, isInvite, requestId) {
		var templateParams = {
			"vs" : locStrings["vs"],
			"gameId" : gameData.gameId,
			"status" : locStrings[gameData.status]
		};
		var elementHtml = templateRenderer.renderTemplate("gameListEntry", templateParams);
		var element = jqueryWrapper.getElement(elementHtml);

		element.find(".playGame").hide();
		element.find(".joinGame").hide();
		element.find(".inviteToGame").hide();
		element.find(".gameOver").hide();

		if ("waiting_for_more_players" == gameData.status) {
			if (isInvite) {
				element.find(".inviteToGame").show();
			} else {
				element.find(".joinGame").show();
			}
		} else {
			element.click(this.buildShowGameDataHandler(gameData.gameId));
			if ("complete" == gameData.status) {
				element.find(".gameOver").show();
			} else if (gameData.currentPlayerId == facebook.getSignedInPlayerId()) {
				element.find(".playGame").show();
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
					var message = "";
					var clickHandler = null;
					if (isInvite) {
						message = locStrings["inviteCTA"];
						clickHandler = this.buildGameInviteClickHandler(gameData.gameId);
					} else {
						message = locStrings["joinCTA"];
						clickHandler = this.buildGameJoinClickHandler(gameData.gameId, teamId, requestId);
					}
					dataNameElement.text(message);
					dataElement.addClass("clickable");
					dataElement.click(clickHandler);
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

	this.buildShowGameDataHandler = function(gameId) {
		return function(event) {
			viewManager.showView("gamePlay", {"gameId" : gameId});
		};
	};

	this.buildGameInviteClickHandler = function(gameId) {
		return function(event) {
			facebook.sendRequests(locStrings["gameInviteTitle"], locStrings["gameInviteMessage"], {"gameId" : gameId});
		};
	};

	this.buildGameJoinClickHandler = function(gameId, teamId, requestId) {
		return function(event) {
			ajax.call("addPlayer", {
				"gameId" : gameId,
				"team" : teamId,
				"playerId" : facebook.getSignedInPlayerId()
			}).done(self.buildHandleJoinGameResponse(requestId));
		};
	};

	this.buildHandleJoinGameResponse = function(requestId) {
		return function(response) {
			if (response.success) {
				facebook.deleteAppRequest(requestId);
			}
			setTimeout(function() {
				viewManager.showView("gameList");
			}, 100);
		};
	};
};

AVOCADO.GameListElementBuilder.getInstance = function(jqueryWrapper, templateRenderer, locStrings, playerNameDirectory, facebook, ajax, viewManager) {
	return new AVOCADO.GameListElementBuilder(jqueryWrapper, templateRenderer, locStrings, playerNameDirectory, facebook, ajax, viewManager);
};