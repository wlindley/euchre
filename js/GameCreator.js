if (AVOCADO == undefined) {
	var AVOCADO = {};
}

AVOCADO.GameCreator = function(fbId, ajax, createGameButton, gameListView) {
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
			gameListView.show();
		}
	}
};

AVOCADO.GameCreator.getInstance = function(fbId, ajax, createGameButton, gameListView) {
	return new AVOCADO.GameCreator(fbId, ajax, createGameButton, gameListView);
};
