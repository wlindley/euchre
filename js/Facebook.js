if (AVOCADO === undefined) {
	var AVOCADO = {};
}

AVOCADO.Facebook = function(jqueryWrapper, appId, channelUrl) {
	var self = this;
	var signedInPlayerId = "";
	var initDeferred = null;
	var getPlayerDataDeferreds = {};

	this.init = function(params) {
		if (null == initDeferred) {
			initDeferred = jqueryWrapper.buildDeferred();
			jqueryWrapper.ajax("//connect.facebook.net/en_US/all.js", {
				"success" : handleAjaxResponse,
				"dataType" : "script",
				"cache" : true
			});
		}
		return initDeferred.promise();
	};

	this.getSignedInPlayerId = function() {
		return signedInPlayerId;
	};

	this.getPlayerData = function(playerId) {
		if (!(playerId in getPlayerDataDeferreds)) {
			var deferred = jqueryWrapper.buildDeferred();
			getPlayerDataDeferreds[playerId] = deferred;
			FB.api("/" + playerId + "?fields=name,id", this.getPlayerDataCallback);
		}
		return getPlayerDataDeferreds[playerId].promise();
	};

	this.getPlayerDataCallback = function(response) {
		var data = {};
		if (!("error" in response)) {
			data["name"] = response["name"];
			data["playerId"] = response["id"];
			getPlayerDataDeferreds[response["id"]].resolve(data);
		}
	};

	function handleAjaxResponse() {
		FB.init({
			"appId" : appId,
			"channelUrl" : channelUrl,
			"status" : true,
			"cookie" : true
		});
		FB.login(handleLoginResponse);
	};

	function handleLoginResponse(response) {
		if (response.authResponse) {
			signedInPlayerId = response.authResponse.userID;
			initDeferred.resolve();
		} else {
			initDeferred.reject();
		}
	};
};

AVOCADO.Facebook.getInstance = function(jqueryWrapper, appId, channelUrl) {
	return new AVOCADO.Facebook(jqueryWrapper, appId, channelUrl);
};