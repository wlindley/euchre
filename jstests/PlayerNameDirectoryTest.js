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
	this.robotPlayerId = "euchre_robot_foo";
	this.robotPlayerName = "Foo Robot";
	this.robotData = [
		{
			"id" : this.robotPlayerId,
			"displayName" : this.robotPlayerName
		}
	];

	this.facebook = mock(AVOCADO.Facebook);
	this.dataRetriever = mock(AVOCADO.DataRetriever);
	this.getPlayerDataPromise = mock(TEST.FakePromise);

	when(this.facebook).getSignedInPlayerId().thenReturn(this.localPlayerId);
	when(this.facebook).getPlayerData(this.playerId).thenReturn(this.getPlayerDataPromise);
	when(this.dataRetriever).get("robots").thenReturn(this.robotData);

	this.buildTestObj();
};

PlayerNameDirectoryTest.prototype.tearDown = function() {
	AVOCADO.PlayerNamePromise.getInstance = this.origPromiseFactory;
};

PlayerNameDirectoryTest.prototype.buildTestObj = function() {
	this.testObj = new AVOCADO.PlayerNameDirectory(this.locStrings, this.facebook, this.dataRetriever);
};

PlayerNameDirectoryTest.prototype.trigger = function(playerId) {
	return this.testObj.getNamePromise(playerId);
};

PlayerNameDirectoryTest.prototype.verifyPlayerNamePromiseParams = function(pid, locStrings) {
	assertEquals(this.playerId, pid);
	assertEquals(this.locStrings, locStrings);
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
	verify(this.facebook).getPlayerData(this.playerId);
	verify(this.getPlayerDataPromise).done(this.testObj.handleResponse);
};

PlayerNameDirectoryTest.prototype.testMultipleCallsToGetNamePromiseOnlyMakeOneServerRequest = function() {
	this.trigger(this.playerId);
	this.trigger(this.playerId);
	verify(this.facebook, once()).getPlayerData(this.playerId);
};

PlayerNameDirectoryTest.prototype.testResponseHandlerSetsNameOnPromise = function() {
	var testHarness = this;
	AVOCADO.PlayerNamePromise.getInstance = function(pid, locStrings) {
		testHarness.verifyPlayerNamePromiseParams(pid, locStrings);
		return mock(AVOCADO.PlayerNamePromise);
	};

	var expectedName = "John Encom";
	when(this.getPlayerDataPromise).done(func()).then(function() {
		testHarness.testObj.handleResponse({
			"playerId" : testHarness.playerId,
			"name" : expectedName
		});
	});

	var promise = this.trigger(this.playerId);

	verify(promise).setName(expectedName);
};

PlayerNameDirectoryTest.prototype.testResponseHandlerGracefullyHandlesUnknownPlayerId = function() {
	var testHarness = this;
	AVOCADO.PlayerNamePromise.getInstance = function(pid, locStrings) {
		testHarness.verifyPlayerNamePromiseParams(pid, locStrings);
		return mock(AVOCADO.PlayerNamePromise);
	};

	when(this.getPlayerDataPromise).done(func()).then(function() {
		testHarness.testObj.handleResponse({});
	});

	var promise = this.trigger(this.playerId);

	verify(promise, never()).setName(anything());
	//verify no exceptions thrown
};

PlayerNameDirectoryTest.prototype.testLocalPlayerIdImmediatelyGetsExpectedName = function() {
	var testHarness = this;
	AVOCADO.PlayerNamePromise.getInstance = function(pid, locStrings) {
		return mock(AVOCADO.PlayerNamePromise);
	};

	var promise = this.trigger(this.localPlayerId);

	verify(this.facebook, never()).getPlayerData(anything(), this.testObj.handleResponse);
	verify(promise).setName(this.expectedYouString);
};

PlayerNameDirectoryTest.prototype.testRobotImmediatelyGetsExpectedName = function() {
	var testHarness = this;
	AVOCADO.PlayerNamePromise.getInstance = function(pid, locStrings) {
		return mock(AVOCADO.PlayerNamePromise);
	};

	var promise = this.trigger(this.robotPlayerId);

	verify(this.facebook, never()).getPlayerData(anything(), this.testObj.handleResponse);
	verify(promise).setName(this.robotPlayerName);
};