if (AVOCADO == undefined) {
	var AVOCADO = {};
}

AVOCADO.GameCreator = function(playerId, ajax, viewManager, templateRenderer, jqueryWrapper) {
	var self = this;

	this.buildGameCreator = function() {
		var element = jqueryWrapper.getElement(templateRenderer.renderTemplate("gameCreator"));
		element.find("#btnCreateGame").click(self.createGameClickHandler);
		return element;
	};

	this.createGameClickHandler = function() {
		setTimeout(function() {
			var params = {
				"playerId" : playerId,
				"team" : 0
			};
			ajax.call("createGame", params, handleCreateGameResponse);
		}, 100);
	};

	function handleCreateGameResponse(response) {
		if (response.success) {
			viewManager.showView("gameList");
		}
	}
};

AVOCADO.GameCreator.getInstance = function(playerId, ajax, viewManager, templateRenderer, jqueryWrapper) {
	return new AVOCADO.GameCreator(playerId, ajax, viewManager, templateRenderer, jqueryWrapper);
};
