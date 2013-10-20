if (AVOCADO == undefined) {
	var AVOCADO = {};
}

AVOCADO.PlayerNamePromise = function (playerId) {
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
			return "";
		}
		return playerName;
	};

	this.getPlayerId = function() {
		return playerId;
	};

	this.registerForUpdates = function(element) {
		elementsToUpdate.push(element);

		if (undefined !== playerName) {
			updateElement(element, playerName);
		}
	};

	function updateElement(element, playerName) {
		element.text(playerName);
	}
};