GameListView = function(gameLister, gameListHtmlBuilder, gameListDiv) {
	var self = this;

	this.show = function() {
		gameLister.getGameList(handleGameListResponse);
	};

	function handleGameListResponse(response) {
		gameListDiv.html(gameListHtmlBuilder.buildHtml(response));
		gameListDiv.show();
	}
};

GameListView.getInstance = function(gameLister, gameListHtmlBuilder, gameListDiv) {
	return new GameListView(gameLister, gameListHtmlBuilder, gameListDiv);
};
