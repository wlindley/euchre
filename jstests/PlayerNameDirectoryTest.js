PlayerNameDirectoryTest = TestCase("PLayerNameDirectoryTest");

PlayerNameDirectoryTest.prototype.setUp = function() {
	this.origPromiseFactory = AVOCADO.PlayerNamePromise.getInstance;

	this.playerId = "2345bcd";
	this.localPlayerId = "mno4567";
	this.expectedYouString = "you string";
	this.locStrings = {
		"you" : this.expectedYouString
	};

	this.ajax = mock(AVOCADO.Ajax);

	this.buildTestObj();
};

PlayerNameDirectoryTest.prototype.tearDown = function() {
	AVOCADO.PlayerNamePromise.getInstance = this.origPromiseFactory;
};

PlayerNameDirectoryTest.prototype.buildTestObj = function() {
	this.testObj = new AVOCADO.PlayerNameDirectory(this.ajax, this.locStrings, this.localPlayerId);
};

PlayerNameDirectoryTest.prototype.trigger = function(playerId) {
	return this.testObj.getNamePromise(playerId);
};

PlayerNameDirectoryTest.prototype.testGetNamePromiseReturnsExpectedPromise = function() {
	var promise = this.trigger(this.playerId);
	assertEquals(this.playerId, promise.getPlayerId());
};

PlayerNameDirectoryTest.prototype.testGetNamePromiseReturnsSamePromiseForMultipleRequestsWithSamePlayerID = function() {
	var promise1 = this.trigger(this.playerId);
	var promise2 = this.trigger(this.playerId);
	assertEquals(promise1, promise2);
};

PlayerNameDirectoryTest.prototype.testGetNamePromiseMakesRequestToServerForName = function() {
	var promise = this.trigger(this.playerId);
	verify(this.ajax).call("getName", allOf(hasMember("playerId", this.playerId)), this.testObj.handleResponse);
};

PlayerNameDirectoryTest.prototype.testMultipleCallsToGetNamePromiseOnlyMakeOneServerRequest = function() {
	this.trigger(this.playerId);
	this.trigger(this.playerId);
	verify(this.ajax, once()).call("getName", allOf(hasMember("playerId", this.playerId)), this.testObj.handleResponse);
};

PlayerNameDirectoryTest.prototype.testResponseHandlerSetsNameOnPromise = function() {
	AVOCADO.PlayerNamePromise.getInstance = function(pid) {
		return mock(AVOCADO.PlayerNamePromise);
	};

	var expectedName = "John Encom";
	this.ajax = new TEST.FakeAjax();
	this.ajax.callbackResponse = {"success" : true, "playerId" : this.playerId, "name" : expectedName};
	this.buildTestObj();

	var promise = this.trigger(this.playerId);

	verify(promise).setName(expectedName);
};

PlayerNameDirectoryTest.prototype.testResponseHandlerGracefullyHandlesUnknownPlayerId = function() {
	AVOCADO.PlayerNamePromise.getInstance = function(pid) {
		return mock(AVOCADO.PlayerNamePromise);
	};

	var expectedName = "Bob Skynet";
	var otherPlayerId = "zxy0987";
	this.ajax = new TEST.FakeAjax();
	this.ajax.callbackResponse = {"success" : true, "playerId" : otherPlayerId, "name" : expectedName};
	this.buildTestObj();

	var promise = this.trigger(this.playerId);

	verify(promise, never()).setName(anything());
	//verify no exceptions thrown
};

PlayerNameDirectoryTest.prototype.testLocalPlayerIdImmediatelyGetsExpectedName = function() {
	AVOCADO.PlayerNamePromise.getInstance = function(pid) {
		return mock(AVOCADO.PlayerNamePromise);
	};

	var promise = this.trigger(this.localPlayerId);

	verify(this.ajax, never()).call("getName", allOf(hasMember("playerId", this.localPlayerId)), this.testObj.handleResponse);
	verify(promise).setName(this.expectedYouString);
};