if (TEST == undefined) {
	var TEST = {};
}

TEST.FakeAjax = function() {
	var self = this;

	this.callbackResponse = null;

	this.call = function(action, data, callback, delay) {
		callback(self.callbackResponse);
	};
};  

TEST.FakeAjax.getInstance = function() {
	return new TEST.FakeAjax();
};
