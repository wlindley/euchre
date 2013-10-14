if (AVOCADO == undefined) {
	var AVOCADO = {};
}

AVOCADO.GameJoiner = function(playerId, ajax, viewManager, templateRenderer, jqueryWrapper) {
	var self = this;

	this.buildGameJoiner = function() {
		var element = jqueryWrapper.getElement(templateRenderer.renderTemplate("gameJoiner"));
		element.find("#btnJoinGame").click(self.buildJoinGameClickHandler(element.find("#txtGameId"), element.find("#txtTeam")));
		return element;
	};

	this.buildJoinGameClickHandler = function(txtGameId, txtTeamId) {
		return function() {
			var data = {
				"gameId" : txtGameId.val(),
				"team" : txtTeamId.val(),
				"playerId" : playerId
			};

			ajax.call("addPlayer", data, handleJoinGameResponse);
		};
	};

	function handleJoinGameResponse(response) {
		if (response.success) {
			viewManager.showView("gameList");
		}
	}
};

AVOCADO.GameJoiner.getInstance = function(playerId, ajax, viewManager, templateRenderer, jqueryWrapper) {
	return new AVOCADO.GameJoiner(playerId, ajax, viewManager, templateRenderer, jqueryWrapper);
};
