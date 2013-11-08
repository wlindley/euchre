if (AVOCADO == undefined) {
	var AVOCADO = {};
}

AVOCADO.GameCompleteDisplayBuilder = function(templateRenderer, jqueryWrapper, locStrings, playerNameDirectory, localPlayerId) {
	var self = this;

	this.buildGameCompleteDisplay = function(teams, scores) {
		var localPlayerTeamId = getTeamIndexByPlayerId(teams, localPlayerId);
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
			gameCompleteElement.addClass("gameLost");
		} else {
			gameCompleteElement.addClass("gameWon");
		}
		for (var i in teams[winningTeamId]) {
			var namePromise = playerNameDirectory.getNamePromise(teams[winningTeamId][i]);
			namePromise.registerForUpdates(gameCompleteElement.find(".winner" + i));
		}

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
};

AVOCADO.GameCompleteDisplayBuilder.getInstance = function(templateRenderer, jqueryWrapper, locStrings, playerNameDirectory, localPlayerId) {
	return new AVOCADO.GameCompleteDisplayBuilder(templateRenderer, jqueryWrapper, locStrings, playerNameDirectory, localPlayerId);
}