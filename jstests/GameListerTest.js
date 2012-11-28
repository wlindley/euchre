GameListerTest = TestCase("GameListerTest")

GameListerTest.prototype.setUp = function() {
	this.fbId = "12345";
	this.ajax = new TEST.FakeAjax();
	this.buildTestObj();
};

GameListerTest.prototype.testListsGamesFromServer = function() {
	var responseData = {"foo" : "bar"};
	this.ajax.callbackResponse = responseData;
	var wasCalled = false;
	var callback = function(data) {
		if (responseData == data) {
			wasCalled = true;
		}
	};
	this.testObj.getGameList(callback);
	assertTrue(wasCalled);
};

GameListerTest.prototype.testCallsAjaxCorrectly = function() {
	this.ajax = mock(AVOCADO.Ajax);
	this.buildTestObj();
	var callback = function(data) {};
	this.testObj.getGameList(callback);
	verify(this.ajax).call("listGames", hasMember("playerId", equalTo(this.fbId)), callback);
};

GameListerTest.prototype.buildTestObj = function() {
	this.testObj = AVOCADO.GameLister.getInstance(this.fbId, this.ajax);
};
