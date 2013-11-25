if (TEST == undefined) {
	TEST = {};
}

TEST.FakeDeferred = function() {
	this.done = function() {};
	this.fail = function() {};
	this.progress = function() {};
	this.then = function() {};
	this.resolve = function() {};
	this.reject = function() {};
	this.notify = function() {};
	this.promise = function() {};	
};

TEST.FakeDeferred.getInstance = function() {
	return new TEST.FakeDeferred();
};

TEST.FakePromise = function() {
	this.done = function() {};
	this.fail = function() {};
	this.progress = function() {};
	this.then = function() {};
};

TEST.FakePromise.getInstance = function() {
	return new TEST.FakePromise();
}