if (AVOCADO == undefined) {
	var AVOCADO = {};
}

AVOCADO.GameCompleteDisplayBuilder = function(templateRenderer, jqueryWrapper, locStrings, playerNameDirectory, localPlayerId) {
	var self = this;

	this.buildGameCompleteDisplay = function(teams, scores) {
		var localPlayerTeamId = getTeamIndexByPlayerId(teams, localPlayerId);
		var otherTeamId = localPlayerTeamId == 0 ? 1 : 0;

		var winningTeamString = locStrings["yourTeam"];
		if (scores[otherTeamId] > scores[localPlayerTeamId]) {
			winningTeamString = locStrings["otherTeam"];
		}

		var gameCompleteHtml = templateRenderer.renderTemplate("gameComplete", {"winningTeam" : winningTeamString, "won" : locStrings["won"]});
		var gameCompleteElement = jqueryWrapper.getElement(gameCompleteHtml);
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