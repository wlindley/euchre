GameListHtmlBuilder = function() {
	var self = this;

	this.buildHtml = function(gameList) {
		var html = "";
		for (var i = 0; i < gameList.length; i++) {
			var curGame = gameList[i];
			var curHtml = '<div class="gameListEntry">';
			curHtml += '<p>Game id:' + curGame.gameId + '</p>';
			curHtml += '</div>';
			html += curHtml;
		}
		return html;
	};
};

GameListHtmlBuilder.getInstance = function() {
	return new GameListHtmlBuilder();
};
