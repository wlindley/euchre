if (AVOCADO == undefined) {
	var AVOCADO = {};
}

AVOCADO.GameCreatorBuilder = function(facebook, ajax, viewManager, templateRenderer, jqueryWrapper) {
	var self = this;

	this.buildGameCreator = function() {
		var element = jqueryWrapper.getElement(templateRenderer.renderTemplate("gameCreator"));
		element.find("#btnCreateGame").click(self.createGameClickHandler);
		return element;
	};

	this.createGameClickHandler = function() {
		var params = {
			"playerId" : facebook.getSignedInPlayerId(),
			"team" : 0
		};
		ajax.call("createGame", params, handleCreateGameResponse);
	};

	function handleCreateGameResponse(response) {
		if (response.success) {
			setTimeout(function() {
				viewManager.showView("gameList");
			}, 100);
		}
	}
};

AVOCADO.GameCreatorBuilder.getInstance = function(facebook, ajax, viewManager, templateRenderer, jqueryWrapper) {
	return new AVOCADO.GameCreatorBuilder(facebook, ajax, viewManager, templateRenderer, jqueryWrapper);
};
