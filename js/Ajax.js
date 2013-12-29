if (AVOCADO == undefined) { 
	var AVOCADO = {};
}

AVOCADO.Ajax = function(jqueryWrapper, dataRetriever) {
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
		return jqueryWrapper.ajax(dataRetriever.get("ajaxUrl"), params);
	};
};

AVOCADO.Ajax.getInstance = function(jqueryWrapper, dataRetriever) {
	return new AVOCADO.Ajax(jqueryWrapper, dataRetriever);
};
