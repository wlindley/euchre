JQueryWrapperTest = TestCase("JQueryWrapperTest")

JQueryWrapperTest.prototype.setUp = function() {
	this.fbId = "12345";
	this.ajax = mock(Ajax);
	this.testObj = GameLister.getInstance(this.fbId, this.ajax);
};

JQueryWrapperTest.prototype.testListsGamesFromServer = function() {
	assertTrue(true);
};
