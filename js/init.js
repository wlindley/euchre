$(function() {
	function createObjects() {
		window.jqueryWrapper = AVOCADO.JQueryWrapper.getInstance($);
		window.ajax = AVOCADO.Ajax.getInstance(window.jqueryWrapper, EUCHRE.ajaxUrl);
		window.templateRenderer = AVOCADO.TemplateRenderer.getInstance(EUCHRE.templates);
		window.gameLister = AVOCADO.GameLister.getInstance(EUCHRE.playerId, window.ajax);
		window.gameListView = AVOCADO.GameListView.getInstance(window.gameLister, window.templateRenderer, $('#gameList'));
		window.gameCreator = AVOCADO.GameCreator.getInstance(EUCHRE.playerId, window.ajax, $('#btnCreateGame'));
		window.gameJoiner = AVOCADO.GameJoiner.getInstance(EUCHRE.playerId, window.ajax, $("#txtGameId"), $("#txtTeam"), $("#btnJoinGame"));
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
