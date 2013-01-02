$(function() {
	function createObjects() {
		window.jqueryWrapper = AVOCADO.JQueryWrapper.getInstance($);
		window.ajax = AVOCADO.Ajax.getInstance(window.jqueryWrapper, EUCHRE.ajaxUrl);
		window.templateRenderer = AVOCADO.TemplateRenderer.getInstance(EUCHRE.templates);
		window.viewManager = AVOCADO.ViewManager.getInstance();
		window.gameLister = AVOCADO.GameLister.getInstance(EUCHRE.playerId, window.ajax);
		window.gameListView = AVOCADO.GameListView.getInstance(window.gameLister, window.templateRenderer, $('#gameList'), window.jqueryWrapper, window.viewManager, EUCHRE.locStrings, EUCHRE.playerId);
		window.gameCreator = AVOCADO.GameCreator.getInstance(EUCHRE.playerId, window.ajax, $('#btnCreateGame'), window.gameListView);
		window.gameJoiner = AVOCADO.GameJoiner.getInstance(EUCHRE.playerId, window.ajax, $("#txtGameId"), $("#txtTeam"), $("#btnJoinGame"), window.gameListView);
		window.gamePlayView = AVOCADO.GamePlayView.getInstance(window.ajax, EUCHRE.playerId, window.templateRenderer, $('#gamePlay'), window.viewManager, EUCHRE.locStrings, window.jqueryWrapper);
	}

	function initObjects() {
		window.gameCreator.init();
		window.gameJoiner.init();
		window.gameListView.init();
		window.gamePlayView.init();
	}


	createObjects();
	initObjects();
	$(".title").addClass("titleLoaded");
	window.gameListView.show();
});
