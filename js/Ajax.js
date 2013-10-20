if (AVOCADO == undefined) { 
	var AVOCADO = {};
}

AVOCADO.Ajax = function(jqueryWrapper, ajaxUrl) {
	var self = this;

	this.call = function(action, data, callback, delay) {
		if (delay) {
			setTimeout(function() {
				doAjax(action, data, callback);
			}, delay);
		} else {
			doAjax(action, data, callback);
		}
	};

	function doAjax(action, data, callback) {
		var finalData = {};
		for (var key in data) {
			finalData[key] = data[key];
		}
		finalData["action"] = action;
		var params = {
			"type" : 'POST',
			"dataType" : 'json',
			"data" : finalData,
			"success" : callback
		};
		jqueryWrapper.ajax(ajaxUrl, params);
	}
};

AVOCADO.Ajax.getInstance = function(jqueryWrapper, ajaxUrl) {
	return new AVOCADO.Ajax(jqueryWrapper, ajaxUrl);
};
