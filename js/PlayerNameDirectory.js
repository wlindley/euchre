if (AVOCADO == undefined) {
	AVOCADO = {};
}

AVOCADO.PlayerNameDirectory = function(locStrings, facebook, dataRetriever) {
	var promises = {};

	this.getNamePromise = function(pid) {
		if (!(pid in promises)) {
			promises[pid] = AVOCADO.PlayerNamePromise.getInstance(pid, locStrings);
			if (facebook.getSignedInPlayerId() == pid) {
				promises[pid].setName(locStrings["you"]);
			} else {
				var displayName = null;
				var robots = dataRetriever.get("robots");
				for (var i in robots) {
					if (pid == robots[i].id) {
						displayName = robots[i].displayName;
					}
				}
				if (null != displayName) {
					promises[pid].setName(displayName);
				} else {
					facebook.getPlayerData(pid).done(this.handleResponse);
				}
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

AVOCADO.PlayerNameDirectory.getInstance = function(locStrings, facebook, dataRetriever) {
	return new AVOCADO.PlayerNameDirectory(locStrings, facebook, dataRetriever);
};