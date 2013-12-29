if (AVOCADO == undefined) {
	var AVOCADO = {};
}

AVOCADO.GameCompleteDisplayBuilder = function(templateRenderer, jqueryWrapper, locStrings, playerNameDirectory, facebook, ajax, viewManager) {
	var self = this;

	this.buildGameCompleteDisplay = function(teams, scores, gameId) {
		var gameCompleteElement = buildElement();
		var winningTeamId = findAndDisplayWinner(gameCompleteElement, teams, scores);
		hookUpNamePromises(gameCompleteElement, teams, winningTeamId);

		gameCompleteElement.find(".dismissButton").click(self.buildDismissClickHandler(gameId));

		return gameCompleteElement;
	};

	function buildElement() {
		var gameCompleteHtml = templateRenderer.renderTemplate("gameComplete", {
			"won" : locStrings["won"],
			"and" : locStrings["and"],
			"dismiss" : locStrings["dismiss"]
		});
		return jqueryWrapper.getElement(gameCompleteHtml);
	}

	function findAndDisplayWinner(gameCompleteElement, teams, scores) {
		var localPlayerTeamId = getTeamIndexByPlayerId(teams, facebook.getSignedInPlayerId());
		var otherTeamId = localPlayerTeamId == 0 ? 1 : 0;
		var winningTeamId = localPlayerTeamId;
		if (scores[otherTeamId] > scores[localPlayerTeamId]) {
			winningTeamId = otherTeamId;
			gameCompleteElement.addClass("red");
		} else {
			gameCompleteElement.addClass("green");
		}
		return winningTeamId;
	}

	function hookUpNamePromises(gameCompleteElement, teams, winningTeamId) {
		for (var i in teams[winningTeamId]) {
			var namePromise = playerNameDirectory.getNamePromise(teams[winningTeamId][i]);
			namePromise.registerForUpdates(gameCompleteElement.find(".winner" + i));
		}
	}

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