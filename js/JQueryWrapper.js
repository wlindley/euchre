JQueryWrapper = function(jquery) {
	var self = this;

	this.ajax = function(url, params) {
		jquery.ajax(url, params);
	};
};

JQueryWrapper.getInstance = function(jquery) {
	return new JQueryWrapper(jquery);
};
