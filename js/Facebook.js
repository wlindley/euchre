if (AVOCADO === undefined) {
	var AVOCADO = {};
}

AVOCADO.StandardFacebookLoginStrategy = function() {
	this.login = function(callback) {
		FB.Event.subscribe("auth.authResponseChange", callback);
	};
};

AVOCADO.StandardFacebookLoginStrategy.getInstance = function() {
	return new AVOCADO.StandardFacebookLoginStrategy();
};

AVOCADO.LocalFacebookLoginStrategy = function() {
	this.login = function(callback) {
		FB.login(callback);
	};
};

AVOCADO.LocalFacebookLoginStrategy.getInstance = function() {
	return new AVOCADO.LocalFacebookLoginStrategy();
};

AVOCADO.FacebookRequest = function(requestId, gameId, message) {
	this.requestId = requestId;
	this.gameId = gameId;
	this.message = message;
};

AVOCADO.FacebookRequest.getInstance = function(jqueryWrapper, rawRequest) {
	var data = jqueryWrapper.jsonDecode(rawRequest["data"]);
	return new AVOCADO.FacebookRequest(rawRequest["id"], data["gameId"], rawRequest["message"]);
};

AVOCADO.Facebook = function(jqueryWrapper, appId, channelUrl, loginStrategy) {
	var self = this;
	var signedInPlayerId = "";
	var initDeferred = null;
	var getPlayerDataDeferreds = {};
	var loginAttempts = 0;

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

	function handleAjaxResponse() {
		FB.init({
			"appId" : appId,
			"channelUrl" : channelUrl,
			"status" : true,
			"cookie" : true,
			"frictionlessRequests" : true
		});
		loginStrategy.login(handleLoginResponse);
	};

	function handleLoginResponse(response) {
		if ("connected" == response.status) {
			signedInPlayerId = response.authResponse.userID;
			initDeferred.resolve();
		} else {
			if (0 == loginAttempts) {
				loginAttempts++;
				FB.login();
			} else {
				initDeferred.reject();
			}
		}
	};

	this.getPlayerData = function(playerId) {
		if (!(playerId in getPlayerDataDeferreds)) {
			var deferred = jqueryWrapper.buildDeferred();
			getPlayerDataDeferreds[playerId] = deferred;
			FB.api("/" + playerId + "?fields=name,id,first_name,last_name", this.getPlayerDataCallback);
		}
		return getPlayerDataDeferreds[playerId].promise();
	};

	this.getPlayerDataCallback = function(response) {
		var data = {};
		if (!response.hasOwnProperty("error")) {
			data["name"] = response["first_name"] + " " + response["last_name"][0] + ".";
			data["playerId"] = response["id"];
			getPlayerDataDeferreds[response["id"]].resolve(data);
		}
	};

	this.getSignedInPlayerId = function() {
		return signedInPlayerId;
	};

	this.sendRequests = function(title, message, data) {
		var deferred = jqueryWrapper.buildDeferred();
		FB.ui({
			"method" : "apprequests",
			"app_id" : appId,
			"title" : title,
			"message" : message,
			"data" : data
		}, this.buildSendRequestsCallback(deferred));
		return deferred.promise();
	};

	this.buildSendRequestsCallback = function(deferred) {
		return function(requestId, toList) {
			if (null === requestId) {
				deferred.reject();
			} else {
				deferred.resolve(toList);
			}
		};
	};

	this.getAppRequests = function() {
		var deferred = jqueryWrapper.buildDeferred();
		FB.api("/" + signedInPlayerId + "/apprequests", this.buildGetAppRequestsCallback(deferred));
		return deferred.promise();
	};

	this.buildGetAppRequestsCallback = function(deferred) {
		return function(response) {
			requests = [];
			for (var i in response.data) {
				requests.push(AVOCADO.FacebookRequest.getInstance(jqueryWrapper, response.data[i]));
			}
			deferred.resolve(requests);
		};
	};

	this.deleteAppRequest = function(requestId) {
		var deferred = jqueryWrapper.buildDeferred();
		FB.api("/" + requestId, "delete", this.buildDeleteAppRequestCallback(deferred));
		return deferred.promise();
	};

	this.buildDeleteAppRequestCallback = function(deferred) {
		return function(response) {
			if (response.hasOwnProperty("error")) {
				deferred.reject();
			} else {
				deferred.resolve();
			}
		};
	};
};

AVOCADO.Facebook.getInstance = function(jqueryWrapper, appId, channelUrl, environment) {
	var loginStrategy = null;
	if ("local" == environment) {
		loginStrategy = AVOCADO.LocalFacebookLoginStrategy.getInstance();
	} else {
		loginStrategy = AVOCADO.StandardFacebookLoginStrategy.getInstance();
	}
	return new AVOCADO.Facebook(jqueryWrapper, appId, channelUrl, loginStrategy);
};