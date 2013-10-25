if (AVOCADO == undefined) {
	var AVOCADO = {};
}

AVOCADO.PlayerNamePromise = function (playerId, locStrings) {
	var playerName = undefined;
	var elementsToUpdate = [];

	this.setName = function(name) {
		playerName = name;
		for (var i in elementsToUpdate) {
			updateElement(elementsToUpdate[i], playerName);
		}
	};

	this.getName = function() {
		if (undefined === playerName) {
			return locStrings["someone"];
		}
		return playerName;
	};

	this.getPlayerId = function() {
		return playerId;
	};

	this.registerForUpdates = function(element) {
		elementsToUpdate.push(element);

		if (undefined === playerName) {
			updateElement(element, locStrings["someone"]);
		} else {
			updateElement(element, playerName);
		}
	};

	function updateElement(element, playerName) {
		element.text(playerName);
	}
};

AVOCADO.PlayerNamePromise.getInstance = function(playerId, locStrings) {
	return new AVOCADO.PlayerNamePromise(playerId, locStrings);
};