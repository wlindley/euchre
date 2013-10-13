if (AVOCADO == undefined) {
	var AVOCADO = {};
}

AVOCADO.GameCreator = function(playerId, ajax, createGameButton, viewManager) {
	var self = this;

	this.init = function() {
		createGameButton.click(self.createGame);
	};

	this.createGame = function() {
		var params = {
			"playerId" : playerId,
			"team" : 0
		};
		ajax.call("createGame", params, handleCreateGameResponse);
	};

	function handleCreateGameResponse(response) {
		if (response.success) {
			viewManager.showView("gameList");
		}
	}
};

AVOCADO.GameCreator.getInstance = function(playerId, ajax, createGameButton, viewManager) {
	return new AVOCADO.GameCreator(playerId, ajax, createGameButton, viewManager);
};
