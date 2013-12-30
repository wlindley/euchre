$(function() {
	function createObjects() {
		window.jqueryWrapper = AVOCADO.JQueryWrapper.getInstance($);
		window.dataRetriever = AVOCADO.DataRetriever.getInstance(EUCHRE);
		window.facebook = AVOCADO.Facebook.getInstance(window.jqueryWrapper, window.dataRetriever);
		window.ajax = AVOCADO.Ajax.getInstance(window.jqueryWrapper, window.dataRetriever);
		window.templateRenderer = AVOCADO.TemplateRenderer.getInstance(window.dataRetriever);
		window.playerNameDirectory = AVOCADO.PlayerNameDirectory.getInstance(EUCHRE.locStrings, window.facebook, window.dataRetriever);
		window.viewManager = AVOCADO.ViewManager.getInstance();
		window.teamUtils = AVOCADO.TeamUtils.getInstance(window.facebook);
		window.gameListView = AVOCADO.GameListView.getInstance(window.templateRenderer, $('#gameList'), window.jqueryWrapper, window.viewManager, window.ajax, EUCHRE.locStrings, window.facebook, window.playerNameDirectory, window.dataRetriever, window.teamUtils);
		window.gamePlayView = AVOCADO.GamePlayView.getInstance(window.ajax, window.facebook, window.templateRenderer, $('#gamePlay'), window.viewManager, EUCHRE.locStrings, window.jqueryWrapper, window.playerNameDirectory, window.teamUtils);
	}

	function initObjects() {
		window.gameListView.init();
		window.gamePlayView.init();
	}

	createObjects();
	window.facebook.init().done(function() {
		initObjects();
		window.gameListView.show();
	});
});
