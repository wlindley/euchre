if (AVOCADO == undefined) {
	var AVOCADO = {};
}

AVOCADO.GameJoinerBuilder = function(playerId, ajax, viewManager, templateRenderer, jqueryWrapper) {
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
			setTimeout(function() {
				viewManager.showView("gameList");
			}, 100);
		}
	}
};

AVOCADO.GameJoinerBuilder.getInstance = function(playerId, ajax, viewManager, templateRenderer, jqueryWrapper) {
	return new AVOCADO.GameJoinerBuilder(playerId, ajax, viewManager, templateRenderer, jqueryWrapper);
};