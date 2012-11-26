$(function() {
	window.jqueryWrapper = JQueryWrapper.getInstance($);
	window.ajax = Ajax.getInstance(window.jqueryWrapper, EUCHRE.ajaxUrl);
	window.gameLister = GameLister.getInstance(window.ajax, EUCHRE.playerId);


	$(".title").addClass("titleLoaded");
});
