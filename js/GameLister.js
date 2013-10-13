if (AVOCADO == undefined) {
	var AVOCADO = {};
}

AVOCADO.GameLister = function(playerId, ajax) {
	var self = this;

	this.getGameList = function(callback) {
		ajax.call("listGames", {"playerId" : playerId}, callback);
	};
};

AVOCADO.GameLister.getInstance = function(playerId, ajax) {
	return new AVOCADO.GameLister(playerId, ajax);
};
