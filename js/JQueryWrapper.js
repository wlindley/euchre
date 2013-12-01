if (AVOCADO == undefined) {
	var AVOCADO = {};
}

AVOCADO.JQueryWrapper = function(jquery) {
	var self = this;

	this.ajax = function(url, params) {
		return jquery.ajax(url, params);
	};

	this.getElement = function(elementOrSelector) {
		return jquery(elementOrSelector);
	};

	this.buildDeferred = function() {
		return jquery.Deferred();
	};

	this.jsonDecode = function(json) {
		return jquery.parseJSON(json);
	};
};

AVOCADO.JQueryWrapper.getInstance = function(jquery) {
	return new AVOCADO.JQueryWrapper(jquery);
};
