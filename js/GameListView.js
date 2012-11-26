GameListView = function(gameLister, gameListHtmlBuilder, gameListDiv) {
	var self = this;

	this.show = function() {
		gameLister.getGameList(handleGameListResponse);
	};

	function handleGameListResponse(response) {
		gameListDiv.html(gameListHtmlBuilder.buildHtml(response.games));
		gameListDiv.show();
	}
};

GameListView.getInstance = function(gameLister, gameListDiv) {
	return new GameListView(gameLister, GameListHtmlBuilder.getInstance(), gameListDiv);
};
