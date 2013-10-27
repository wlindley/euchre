if (AVOCADO == undefined) {
	var AVOCADO = {};
}

AVOCADO.GameListView = function(gameLister, templateRenderer, gameListDiv, jqueryWrapper, viewManager, ajax, locStrings, playerId, gameCreator, gameJoiner, playerNameDirectory) {
	var self = this;

	this.init = function() {
		viewManager.registerView("gameList", self);
	};

	this.show = function() {
		gameLister.getGameList(handleGameListResponse);
	};

	this.hide = function() {
		gameListDiv.hide();
	};

	function handleGameListResponse(response) {
		gameListDiv.empty();
		gameListDiv.append(templateRenderer.renderTemplate("gameListHeader"));
		for (var i = 0; i < response.games.length; i++) {
			var gameHtml = templateRenderer.renderTemplate("gameListEntry", buildTemplateValues(response.games[i]));
			var element = jqueryWrapper.getElement(gameHtml);

			if (response.games[i].status != "waiting_for_more_players") {
				element.find(".viewGameData").click(self.showGameData);
			} else {
				element.removeClass("gameListEntryClickable");
			}
			if (response.games[i].currentPlayerId != playerId) {
				element.removeClass("gameListEntryYourTurn");
			}

			var nameElement = element.find(".turn").find(".playerName");
			if (null == response.games[i].currentPlayerId) {
				nameElement.text(locStrings["n/a"]);
			} else {
				var namePromise = playerNameDirectory.getNamePromise(response.games[i].currentPlayerId);
				namePromise.registerForUpdates(nameElement);
			}

			var playerTable = element.find(".gameListElementTeams");
			for (var teamId = 0; teamId < 2; teamId++) {
				for (var index = 0; index < 2; index++) {
					var dataElement = playerTable.find("td").has("input.team[value=" + teamId + "]").has("input.index[value=" + index + "]");
					var dataNameElement = dataElement.find(".playerName");
					if ((teamId in response.games[i].teams) && (index in response.games[i].teams[teamId])) {
						var namePromise = playerNameDirectory.getNamePromise(response.games[i].teams[teamId][index]);
						namePromise.registerForUpdates(dataNameElement);
					} else {
						dataNameElement.text(locStrings["inviteCTA"]);
					}
				}
			}

			element.appendTo(gameListDiv);
		}

		var gameCreatorElement = gameCreator.buildGameCreator();
		gameListDiv.append(gameCreatorElement);

		var gameJoinerElement = gameJoiner.buildGameJoiner();
		gameListDiv.append(gameJoinerElement);

		gameListDiv.show();
	}

	function buildTemplateValues(gameData) {
		var values = {
			"gameId" : gameData.gameId,
			"status" : gameData.status
		};
		return values;
	}

	this.showGameData = function(event) {
		gameListDiv.hide();
		var target = jqueryWrapper.getElement(event.currentTarget);
		var gameId = target.attr("id").replace("gameId_", "");
		viewManager.showView("gamePlay", {"gameId" : gameId});
	};
};

AVOCADO.GameListView.getInstance = function(templateRenderer, gameListDiv, jqueryWrapper, viewManager, ajax, locStrings, playerId, playerNameDirectory) {
	var gameLister = new AVOCADO.GameLister.getInstance(playerId, ajax);
	var gameCreator = new AVOCADO.GameCreatorBuilder.getInstance(playerId, ajax, viewManager, templateRenderer, jqueryWrapper);
	var gameJoiner = new AVOCADO.GameJoinerBuilder.getInstance(playerId, ajax, viewManager, templateRenderer, jqueryWrapper);
	return new AVOCADO.GameListView(gameLister, templateRenderer, gameListDiv, jqueryWrapper, viewManager, ajax, locStrings, playerId, gameCreator, gameJoiner, playerNameDirectory);
};
