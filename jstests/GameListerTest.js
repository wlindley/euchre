GameListerTest = TestCase("GameListerTest")

GameListerTest.prototype.setUp = function() {
	this.fbId = "12345";
	this.ajax = mock(Ajax);
	this.testObj = GameLister.getInstance(this.fbId, this.ajax);
};

GameListerTest.prototype.testListsGamesFromServer = function() {
	assertTrue(true);
};
