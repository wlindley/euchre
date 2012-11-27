$(function() {
	function createObjects() {
		window.jqueryWrapper = JQueryWrapper.getInstance($);
		window.ajax = Ajax.getInstance(window.jqueryWrapper, EUCHRE.ajaxUrl);
		window.templateRenderer = TemplateRenderer.getInstance(EUCHRE.templates);
		window.gameLister = GameLister.getInstance(EUCHRE.playerId, window.ajax);
		window.gameListView = GameListView.getInstance(window.gameLister, window.templateRenderer, $('#gameList'));
		window.gameCreator = GameCreator.getInstance(EUCHRE.playerId, window.ajax, $('#btnCreateGame'));
	}

	function initObjects() {
		window.gameCreator.init();
	}


	createObjects();
	initObjects();
	$(".title").addClass("titleLoaded");
	window.gameListView.show();
});
