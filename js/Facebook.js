if (AVOCADO === undefined) {
	var AVOCADO = {};
}

AVOCADO.Facebook = function(jqueryWrapper, appId, channelUrl) {
	var self = this;
	var successCallback = null;
	var failureCallback = null;

	this.init = function(params) {
		successCallback = params["success"];
		failureCallback = params["failure"];
		jqueryWrapper.ajax("//connect.facebook.net/en_US/all.js", {
			"success" : self.handleAjaxResponse,
			"dataType" : "script",
			"cache" : true
		});
	};

	this.handleAjaxResponse = function() {
		FB.init({
			"appId" : appId,
			"channelUrl" : channelUrl,
			"status" : true,
			"cookie" : true
		});
		FB.login(self.handleLoginResponse);
	};

	this.handleLoginResponse = function(response) {
		if (response.authResponse) {
			if (successCallback) {
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