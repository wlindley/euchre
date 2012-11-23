GameLister = function(fbId, ajax) {
	var self = this;

	this.getGameList = function() {
		return null;
	}
};

GameLister.getInstance = function(fbId, ajax) {
	return new GameLister(fbId, ajax);
};
