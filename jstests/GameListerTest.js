GameListerTest = TestCase("GameListerTest")

GameListerTest.prototype.setUp = function() {
	this.fbId = "12345";
	this.ajax = new TEST.FakeAjax();
	this.facebook = mock(AVOCADO.Facebook);

	when(this.facebook).getSignedInPlayerId().thenReturn(this.fbId);

	this.buildTestObj();
};

GameListerTest.prototype.testListsGamesFromServer = function() {
	var wasCalled = false;
	var responseData = {"foo" : "bar"};
	var callback = function(data) {
		if (responseData == data) {
			wasCalled = true;
		}
	};
	this.testObj.getGameList().done(callback);
	this.ajax.resolveCall(responseData);

	assertTrue(wasCalled);
};

GameListerTest.prototype.testCallsAjaxCorrectly = function() {
	this.ajax = mock(AVOCADO.Ajax);
	this.buildTestObj();

	this.testObj.getGameList();

	verify(this.ajax).call("listGames", hasMember("playerId", equalTo(this.fbId)));
};

GameListerTest.prototype.buildTestObj = function() {
	this.testObj = AVOCADO.GameLister.getInstance(this.facebook, this.ajax);
};
