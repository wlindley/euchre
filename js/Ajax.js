Ajax = function(jqueryWrapper, ajaxUrl) {
	var self = this;

	this.call = function(action, data, callback) {
		var finalData = {};
		for (var key in data) {
			finalData[key] = data[key];
		}
		finalData["action"] = action;
		var params = {
			"type" : 'POST',
			"data" : finalData,
			"success" : callback
		};
		jqueryWrapper.ajax(ajaxUrl, params);
	};
};

Ajax.getInstance = function(jqueryWrapper, ajaxUrl) {
	return new Ajax(jqueryWrapper, ajaxUrl);
};
