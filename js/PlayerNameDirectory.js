if (AVOCADO == undefined) {
	AVOCADO = {};
}

AVOCADO.PlayerNameDirectory = function(locStrings, facebook) {
	var promises = {};

	this.getNamePromise = function(pid) {
		if (!(pid in promises)) {
			promises[pid] = AVOCADO.PlayerNamePromise.getInstance(pid, locStrings);
			if (facebook.getSignedInPlayerId() == pid) {
				promises[pid].setName(locStrings["you"]);
			} else {
				facebook.getPlayerData(pid, this.handleResponse);
			}
		}
		return promises[pid];
	};

	this.handleResponse = function(response) {
		var pid = response["playerId"];
		if (pid in promises) {
			promises[pid].setName(response["name"]);
		}
	};
};

AVOCADO.PlayerNameDirectory.getInstance = function(locStrings, facebook) {
	return new AVOCADO.PlayerNameDirectory(locStrings, facebook);
};