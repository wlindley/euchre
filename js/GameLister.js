if (AVOCADO == undefined) {
	var AVOCADO = {};
}

AVOCADO.GameLister = function(facebook, ajax) {
	var self = this;

	this.getGameList = function() {
		return ajax.call("listGames", {"playerId" : facebook.getSignedInPlayerId()});
	};
};

AVOCADO.GameLister.getInstance = function(facebook, ajax) {
	return new AVOCADO.GameLister(facebook, ajax);
};
