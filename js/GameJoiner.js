if (AVOCADO == undefined) {
	var AVOCADO = {};
}

AVOCADO.GameJoiner = function(playerId, ajax, txtGameId, txtTeam, btnJoinGame, viewManager) {
	var self = this;

	this.init = function() {
		btnJoinGame.click(self.joinGameFromTextFields);
	};

	this.joinGameFromTextFields = function() {
		var data = {
			"gameId" : txtGameId.val(),
			"team" : txtTeam.val(),
			"playerId" : playerId
		};

		ajax.call("addPlayer", data, handleJoinGameResponse);
	};

	function handleJoinGameResponse(response) {
		if (response.success) {
			viewManager.showView("gameList");
		}
	}
};

AVOCADO.GameJoiner.getInstance = function(playerId, ajax, txtGameId, txtTeam, btnJoinGame, viewManager) {
	return new AVOCADO.GameJoiner(playerId, ajax, txtGameId, txtTeam, btnJoinGame, viewManager);
};
