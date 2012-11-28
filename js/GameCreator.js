if (AVOCADO == undefined) {
	var AVOCADO = {};
}

AVOCADO.GameCreator = function(fbId, ajax, createGameButton) {
	var self = this;

	this.init = function() {
		createGameButton.click(self.createGame);
	};

	this.createGame = function() {
		var params = {
			"playerId" : fbId,
			"team" : 0
		};
		ajax.call("createGame", params, function() {});
	};

	function handleCreateGameResponse(response) {
		//do nothing
	}
};

AVOCADO.GameCreator.getInstance = function(fbId, ajax, createGameButton) {
	return new AVOCADO.GameCreator(fbId, ajax, createGameButton);
};
