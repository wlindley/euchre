if (TEST == undefined) {
	var TEST = {};
}

TEST.FakeAjax = function() {
	var self = this;
	var callDeferred = null;

	this.call = function(action, data) {
		callDeferred = $.Deferred();
		return callDeferred.promise();
	};

	this.resolveCall = function(response) {
		callDeferred.resolve(response);
	};
};  

TEST.FakeAjax.getInstance = function() {
	return new TEST.FakeAjax();
};
