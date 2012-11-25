AjaxTest = TestCase("AjaxTest")

AjaxTest.prototype.setUp = function() {
	this.fbId = "12345";
	this.ajax = mock(Ajax);
	this.testObj = GameLister.getInstance(this.fbId, this.ajax);
};

AjaxTest.prototype.testListsGamesFromServer = function() {
	assertTrue(true);
};
