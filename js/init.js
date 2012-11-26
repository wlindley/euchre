$(function() {
	window.jqueryWrapper = JQueryWrapper.getInstance($);
	window.ajax = Ajax.getInstance(window.jqueryWrapper, EUCHRE.ajaxUrl);
	window.gameLister = GameLister.getInstance(EUCHRE.playerId, window.ajax);
	window.gameListView = GameListView.getInstance(window.gameLister, $('#gameList'));


	$(".title").addClass("titleLoaded");
	window.gameListView.show();
});
