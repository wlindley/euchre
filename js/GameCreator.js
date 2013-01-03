if (AVOCADO == undefined) {
	var AVOCADO = {};
}

AVOCADO.GameCreator = function(fbId, ajax, createGameButton, viewManager) {
	var self = this;

	this.init = function() {
		createGameButton.click(self.createGame);
	};

	this.createGame = function() {
		var params = {
			"playerId" : fbId,
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

AVOCADO.GameCreator.getInstance = function(fbId, ajax, createGameButton, viewManager) {
	return new AVOCADO.GameCreator(fbId, ajax, createGameButton, viewManager);
};
