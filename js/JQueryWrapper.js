if (AVOCADO == undefined) {
	var AVOCADO = {};
}

AVOCADO.JQueryWrapper = function(jquery) {
	var self = this;

	this.ajax = function(url, params) {
		jquery.ajax(url, params);
	};
};

AVOCADO.JQueryWrapper.getInstance = function(jquery) {
	return new AVOCADO.JQueryWrapper(jquery);
};
