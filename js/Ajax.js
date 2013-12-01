if (AVOCADO == undefined) { 
	var AVOCADO = {};
}

AVOCADO.Ajax = function(jqueryWrapper, ajaxUrl) {
	var self = this;

	this.call = function(action, data) {
		var finalData = {};
		for (var key in data) {
			finalData[key] = data[key];
		}
		finalData["action"] = action;
		var params = {
			"type" : 'POST',
			"dataType" : 'json',
			"data" : finalData
		};
		return jqueryWrapper.ajax(ajaxUrl, params);
	};
};

AVOCADO.Ajax.getInstance = function(jqueryWrapper, ajaxUrl) {
	return new AVOCADO.Ajax(jqueryWrapper, ajaxUrl);
};
