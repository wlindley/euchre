if (AVOCADO == undefined) {
	var AVOCADO = {};
}

AVOCADO.TeamUtils = function(facebook) {
	var self = this;

	this.findOpenTeams = function(teams) {
		var openTeams = [];
		for (var i = 0; i < 2; i++) {
			if (teams[i].length < 2) {
				openTeams.push(i);
			}
		}
		return openTeams;
	};

	this.isPlayerOnTeam = function(playerId, team) {
		return -1 != team.indexOf(playerId);
	};

	this.isLocalPlayerOnTeam = function(team) {
		return this.isPlayerOnTeam(facebook.getSignedInPlayerId(), team);
	};

	this.areOnSameTeam = function(teams, firstPlayerId, secondPlayerId) {
		return (-1 == teams[0].indexOf(firstPlayerId)) == (-1 == teams[0].indexOf(secondPlayerId));
	};

	this.isOnLocalPlayersTeam = function(teams, playerId) {
		return this.areOnSameTeam(teams, playerId, facebook.getSignedInPlayerId());
	};

	this.getAllyClass = function() {
		return "green";
	};

	this.getOpponentClass = function() {
		return "red";
	};
};

AVOCADO.TeamUtils.getInstance = function(facebook) {
	return new AVOCADO.TeamUtils(facebook);
}