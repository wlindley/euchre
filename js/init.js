$(function() {
	function createObjects() {
		window.jqueryWrapper = AVOCADO.JQueryWrapper.getInstance($);
		window.ajax = AVOCADO.Ajax.getInstance(window.jqueryWrapper, EUCHRE.ajaxUrl);
		window.templateRenderer = AVOCADO.TemplateRenderer.getInstance(EUCHRE.templates);
		window.gamePlayView = AVOCADO.GamePlayView.getInstance(window.ajax, EUCHRE.playerId, window.templateRenderer, $('#gamePlay'));
		window.gameLister = AVOCADO.GameLister.getInstance(EUCHRE.playerId, window.ajax);
		window.gameListView = AVOCADO.GameListView.getInstance(window.gameLister, window.templateRenderer, $('#gameList'), window.jqueryWrapper, window.gamePlayView);
		window.gameCreator = AVOCADO.GameCreator.getInstance(EUCHRE.playerId, window.ajax, $('#btnCreateGame'), window.gameListView);
		window.gameJoiner = AVOCADO.GameJoiner.getInstance(EUCHRE.playerId, window.ajax, $("#txtGameId"), $("#txtTeam"), $("#btnJoinGame"), window.gameListView);
	}

	function initObjects() {
		window.gameCreator.init();
		window.gameJoiner.init();
	}


	createObjects();
	initObjects();
	$(".title").addClass("titleLoaded");
	window.gameListView.show();
});
