GameLister = function(fbId, ajax) {
	var self = this;

	this.getGameList = function(callback) {
		ajax.call("listGames", {"playerId" : fbId}, callback);
	};
};

GameLister.getInstance = function(fbId, ajax) {
	return new GameLister(fbId, ajax);
};
