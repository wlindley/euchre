if (AVOCADO == undefined) {
	var AVOCADO = {};
}

AVOCADO.GameCompleteDisplayBuilder = function(templateRenderer, jqueryWrapper, locStrings, playerNameDirectory, facebook, ajax, viewManager, teamUtils) {
	var self = this;

	this.buildGameCompleteDisplay = function(teams, scores, gameId) {
		var gameCompleteElement = buildElement();
		var winningTeamId = getWinningTeamId(teams, scores);
		showWinnerColor(gameCompleteElement, teams[winningTeamId]);
		hookUpWinnerNamePromises(gameCompleteElement, teams[winningTeamId]);

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

	function getWinningTeamId(teams, scores) {
		var localPlayerTeamId = teamUtils.getLocalPlayersTeamId(teams);
		var otherTeamId = localPlayerTeamId == 0 ? 1 : 0;
		return (scores[localPlayerTeamId] > scores[otherTeamId]) ? localPlayerTeamId : otherTeamId;
	};

	function showWinnerColor(gameCompleteElement, winningTeam) {
		if (teamUtils.isLocalPlayerOnTeam(winningTeam)) {
			gameCompleteElement.addClass(teamUtils.getAllyClass());
		} else {
			gameCompleteElement.addClass(teamUtils.getOpponentClass());
		}
	}

	function hookUpWinnerNamePromises(gameCompleteElement, winningTeam) {
		for (var i in winningTeam) {
			var namePromise = playerNameDirectory.getNamePromise(winningTeam[i]);
			namePromise.registerForUpdates(gameCompleteElement.find(".winner" + i));
		}
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

AVOCADO.GameCompleteDisplayBuilder.getInstance = function(templateRenderer, jqueryWrapper, locStrings, playerNameDirectory, facebook, ajax, viewManager, teamUtils) {
	return new AVOCADO.GameCompleteDisplayBuilder(templateRenderer, jqueryWrapper, locStrings, playerNameDirectory, facebook, ajax, viewManager, teamUtils);
}