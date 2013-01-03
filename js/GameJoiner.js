if (AVOCADO == undefined) {
	var AVOCADO = {};
}

AVOCADO.GameJoiner = function(fbId, ajax, txtGameId, txtTeam, btnJoinGame, viewManager) {
	var self = this;

	this.init = function() {
		btnJoinGame.click(self.joinGameFromTextFields);
	};

	this.joinGameFromTextFields = function() {
		var data = {
			"gameId" : txtGameId.val(),
			"team" : txtTeam.val(),
			"playerId" : fbId
		};

		ajax.call("addPlayer", data, handleJoinGameResponse);
	};

	function handleJoinGameResponse(response) {
		if (response.success) {
			viewManager.showView("gameList");
		}
	}
};

AVOCADO.GameJoiner.getInstance = function(fbId, ajax, txtGameId, txtTeam, btnJoinGame, viewManager) {
	return new AVOCADO.GameJoiner(fbId, ajax, txtGameId, txtTeam, btnJoinGame, viewManager);
};
