GameListView = function(gameLister, templateRenderer, gameListDiv) {
	var self = this;

	this.show = function() {
		gameLister.getGameList(handleGameListResponse);
	};

	function handleGameListResponse(response) {
		var html = "";
		for (var i = 0; i < response.games.length; i++) {
			html += templateRenderer.renderTemplate("gameListEntry", response.games[i]);
		}
		gameListDiv.html(html);
		gameListDiv.show();
	}
};

GameListView.getInstance = function(gameLister, templateRenderer, gameListDiv) {
	return new GameListView(gameLister, templateRenderer, gameListDiv);
};
