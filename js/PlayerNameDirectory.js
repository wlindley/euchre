if (AVOCADO == undefined) {
	AVOCADO = {};
}

AVOCADO.PlayerNameDirectory = function(ajax, locStrings, playerId) {
	var promises = {};

	this.getNamePromise = function(pid) {
		if (!(pid in promises)) {
			promises[pid] = AVOCADO.PlayerNamePromise.getInstance(pid);
			if (playerId == pid) {
				promises[pid].setName(locStrings["you"]);
			} else {
				ajax.call("getName", {"playerId" : pid}, this.handleResponse);
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

AVOCADO.PlayerNameDirectory.getInstance = function(ajax, locStrings, playerId) {
	return new AVOCADO.PlayerNameDirectory(ajax, locStrings, playerId);
};