if (AVOCADO == undefined) {
	var AVOCADO = {};
}

AVOCADO.GameLister = function(facebook, ajax) {
	var self = this;

	this.getGameList = function(callback) {
		ajax.call("listGames", {"playerId" : facebook.getSignedInPlayerId()}, callback);
	};
};

AVOCADO.GameLister.getInstance = function(facebook, ajax) {
	return new AVOCADO.GameLister(facebook, ajax);
};
