$(function() {
	function createObjects() {
		window.jqueryWrapper = AVOCADO.JQueryWrapper.getInstance($);
		window.facebook = AVOCADO.Facebook.getInstance(window.jqueryWrapper, EUCHRE.appId, EUCHRE.channelUrl);
		window.ajax = AVOCADO.Ajax.getInstance(window.jqueryWrapper, EUCHRE.ajaxUrl);
		window.templateRenderer = AVOCADO.TemplateRenderer.getInstance(EUCHRE.templates);
		window.playerNameDirectory = AVOCADO.PlayerNameDirectory.getInstance(window.ajax, EUCHRE.locStrings, window.facebook);
		window.viewManager = AVOCADO.ViewManager.getInstance();
		window.gameListView = AVOCADO.GameListView.getInstance(window.templateRenderer, $('#gameList'), window.jqueryWrapper, window.viewManager, window.ajax, EUCHRE.locStrings, window.facebook, window.playerNameDirectory);
		window.gamePlayView = AVOCADO.GamePlayView.getInstance(window.ajax, window.facebook, window.templateRenderer, $('#gamePlay'), window.viewManager, EUCHRE.locStrings, window.jqueryWrapper, window.playerNameDirectory);
	}

	function initObjects() {
		window.gameListView.init();
		window.gamePlayView.init();
	}

	createObjects();
	window.facebook.init({"success" : function() {
		initObjects();
		window.gameListView.show();
	}});
	$(".title").addClass("titleLoaded");
});
