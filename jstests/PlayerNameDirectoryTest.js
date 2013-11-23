PlayerNameDirectoryTest = TestCase("PLayerNameDirectoryTest");

PlayerNameDirectoryTest.prototype.setUp = function() {
	this.origPromiseFactory = AVOCADO.PlayerNamePromise.getInstance;

	this.playerId = "2345bcd";
	this.localPlayerId = "mno4567";
	this.expectedYouString = "you string";
	this.locStrings = {
		"you" : this.expectedYouString,
		"someone" : "freeb"
	};

	this.facebook = mock(AVOCADO.Facebook);

	when(this.facebook).getSignedInPlayerId().thenReturn(this.localPlayerId);

	this.buildTestObj();
};

PlayerNameDirectoryTest.prototype.tearDown = function() {
	AVOCADO.PlayerNamePromise.getInstance = this.origPromiseFactory;
};

PlayerNameDirectoryTest.prototype.buildTestObj = function() {
	this.testObj = new AVOCADO.PlayerNameDirectory(this.locStrings, this.facebook);
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
	verify(this.facebook).getPlayerData(this.playerId, this.testObj.handleResponse);
};

PlayerNameDirectoryTest.prototype.testMultipleCallsToGetNamePromiseOnlyMakeOneServerRequest = function() {
	this.trigger(this.playerId);
	this.trigger(this.playerId);
	verify(this.facebook, once()).getPlayerData(this.playerId, this.testObj.handleResponse);
};

PlayerNameDirectoryTest.prototype.testResponseHandlerSetsNameOnPromise = function() {
	AVOCADO.PlayerNamePromise.getInstance = function(pid, locStrings) {
		return mock(AVOCADO.PlayerNamePromise);
	};

	var testHarness = this;
	var expectedName = "John Encom";
	when(this.facebook).getPlayerData(this.playerId, this.testObj.handleResponse).then(function() {
		testHarness.testObj.handleResponse({
			"playerId" : testHarness.playerId,
			"name" : expectedName
		});
	});

	var promise = this.trigger(this.playerId);

	verify(promise).setName(expectedName);
};

PlayerNameDirectoryTest.prototype.testResponseHandlerGracefullyHandlesUnknownPlayerId = function() {
	AVOCADO.PlayerNamePromise.getInstance = function(pid, locStrings) {
		return mock(AVOCADO.PlayerNamePromise);
	};

	var testHarness = this;
	when(this.facebook).getPlayerData(this.playerId, this.testObj.handleResponse).then(function() {
		testHarness.testObj.handleResponse({});
	});

	var promise = this.trigger(this.playerId);

	verify(promise, never()).setName(anything());
	//verify no exceptions thrown
};

PlayerNameDirectoryTest.prototype.testLocalPlayerIdImmediatelyGetsExpectedName = function() {
	AVOCADO.PlayerNamePromise.getInstance = function(pid, locStrings) {
		return mock(AVOCADO.PlayerNamePromise);
	};

	var promise = this.trigger(this.localPlayerId);

	verify(this.facebook, never()).getPlayerData(this.playerId, this.testObj.handleResponse);
	verify(promise).setName(this.expectedYouString);
};