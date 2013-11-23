if (AVOCADO === undefined) {
	var AVOCADO = {};
}

AVOCADO.Facebook = function(jqueryWrapper, appId, channelUrl) {
	var self = this;
	var signedInPlayerId = "";
	var successCallback = null;
	var failureCallback = null;

	this.init = function(params) {
		successCallback = params["success"];
		failureCallback = params["failure"];
		jqueryWrapper.ajax("//connect.facebook.net/en_US/all.js", {
			"success" : handleAjaxResponse,
			"dataType" : "script",
			"cache" : true
		});
	};

	this.getSignedInPlayerId = function() {
		return signedInPlayerId;
	};

	this.getPlayerData = function(playerId, callback) {
		FB.api("/" + playerId + "?fields=name,id", this.buildGetPlayerDataCallback(callback));
	};

	this.buildGetPlayerDataCallback = function(callback) {
		return function(response) {
			var data = {};
			if (!("error" in response)) {
				data["name"] = response["name"];
				data["playerId"] = response["id"];
			}
			callback(data);
		};
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
			if (successCallback) {
				signedInPlayerId = response.authResponse.userID;
				successCallback();
			}
		} else {
			if (failureCallback) {
				failureCallback();
			}
		}
	};
};

AVOCADO.Facebook.getInstance = function(jqueryWrapper, appId, channelUrl) {
	return new AVOCADO.Facebook(jqueryWrapper, appId, channelUrl);
};