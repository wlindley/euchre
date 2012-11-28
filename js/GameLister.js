if (AVOCADO == undefined) {
	var AVOCADO = {};
}

AVOCADO.GameLister = function(fbId, ajax) {
	var self = this;

	this.getGameList = function(callback) {
		ajax.call("listGames", {"playerId" : fbId}, callback);
	};
};

AVOCADO.GameLister.getInstance = function(fbId, ajax) {
	return new AVOCADO.GameLister(fbId, ajax);
};
