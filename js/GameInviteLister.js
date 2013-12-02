if (AVOCADO == undefined) {
	var AVOCADO = {};
}

AVOCADO.GameInviteLister = function(facebook, ajax, jqueryWrapper) {
	this.getGameInviteList = function() {
		var deferred = jqueryWrapper.buildDeferred();
		facebook.getAppRequests().done(buildGetRequestsHandler(deferred));
		return deferred.promise();
	};

	function buildGetRequestsHandler(deferred) {
		return function(requests) {
			var gameIds = "[";
			for (var i in requests) {
				gameIds += '"' + requests[i].gameId + '"';
				if (i != requests.length - 1) {
					gameIds += ", ";
				}
			}
			gameIds += "]";
			ajax.call("getBasicGameData", {"gameIds" : gameIds}).done(buildAjaxResponseHandler(deferred));
		};
	};

	function buildAjaxResponseHandler(deferred) {
		return function(response) {
			deferred.resolve(response.games);
		};
	};
};

AVOCADO.GameInviteLister.getInstance = function(facebook, ajax, jqueryWrapper) {
	return new AVOCADO.GameInviteLister(facebook, ajax, jqueryWrapper);
};