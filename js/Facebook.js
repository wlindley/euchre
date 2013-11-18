if (AVOCADO === undefined) {
	var AVOCADO = {};
}

AVOCADO.Facebook = function(jqueryWrapper, appId, channelUrl) {
	var self = this;

	this.init = function() {
		jqueryWrapper.ajax("//connect.facebook.net/en_US/all.js", {
			"success" : this.handleAjaxResponse,
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
		FB.login();
	};
};

AVOCADO.Facebook.getInstance = function(jqueryWrapper, appId, channelUrl) {
	return new AVOCADO.Facebook(jqueryWrapper, appId, channelUrl);
};