if (AVOCADO == undefined) {
	var AVOCADO = {};
}

AVOCADO.GameCompleteDisplayBuilder = function(templateRenderer, jqueryWrapper, locStrings, playerNameDirectory, facebook, ajax, viewManager) {
	var self = this;

	this.buildGameCompleteDisplay = function(teams, scores, gameId) {
		var localPlayerTeamId = getTeamIndexByPlayerId(teams, facebook.getSignedInPlayerId());
		var otherTeamId = localPlayerTeamId == 0 ? 1 : 0;

		var gameCompleteHtml = templateRenderer.renderTemplate("gameComplete", {
			"won" : locStrings["won"],
			"and" : locStrings["and"],
			"dismiss" : locStrings["dismiss"]
		});
		var gameCompleteElement = jqueryWrapper.getElement(gameCompleteHtml);

		var winningTeamId = localPlayerTeamId;
		if (scores[otherTeamId] > scores[localPlayerTeamId]) {
			winningTeamId = otherTeamId;
			gameCompleteElement.addClass("red");
		} else {
			gameCompleteElement.addClass("green");
		}
		for (var i in teams[winningTeamId]) {
			var namePromise = playerNameDirectory.getNamePromise(teams[winningTeamId][i]);
			namePromise.registerForUpdates(gameCompleteElement.find(".winner" + i));
		}

		gameCompleteElement.find(".dismissButton").click(self.buildDismissClickHandler(gameId));

		return gameCompleteElement;
	};

	function getTeamIndexByPlayerId(teams, playerId) {
		for (var teamIndex in teams) {
			if (-1 != teams[teamIndex].indexOf(playerId)) {
				return teamIndex;
			}
		}
		return -1;
	}

	this.buildDismissClickHandler = function(gameId) {
		return function() {
			ajax.call("dismissCompletedGame", {"gameId" : gameId, "playerId" : facebook.getSignedInPlayerId()}).done(handleDismissResponseHandler);
		};
	};

	function handleDismissResponseHandler(response) {
		setTimeout(function() {
			viewManager.showView("gameList");
		}, 100);
	}
};

AVOCADO.GameCompleteDisplayBuilder.getInstance = function(templateRenderer, jqueryWrapper, locStrings, playerNameDirectory, facebook, ajax, viewManager) {
	return new AVOCADO.GameCompleteDisplayBuilder(templateRenderer, jqueryWrapper, locStrings, playerNameDirectory, facebook, ajax, viewManager);
}