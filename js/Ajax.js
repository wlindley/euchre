Ajax = function(jqueryWrapper) {
	var self = this;

	this.call = function(action, data, callback) {
	};
};

Ajax.getInstance = function(jqueryWrapper) {
	return new Ajax(jqueryWrapper);
};
