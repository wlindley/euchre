FakeAjax = function() {
	var self = this;

	this.callbackResponse = null;

	this.call = function(action, data, callback) {
		callback(self.callbackResponse);
	};
};  

FakeAjax.getInstance = function() {
	return new FakeAjax();
};
