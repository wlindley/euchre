PlayerNamePromiseTest = TestCase("PlayerNamePromiseTest");

PlayerNamePromiseTest.prototype.setUp = function() {
	this.playerId = "12345abc";

	this.buildTestObj();
};

PlayerNamePromiseTest.prototype.buildTestObj = function() {
	this.testObj = new AVOCADO.PlayerNamePromise(this.playerId);
};

PlayerNamePromiseTest.prototype.testGetPlayerIdReturnsExpectedPlayerId = function() {
	assertEquals(this.playerId, this.testObj.getPlayerId());
};

PlayerNamePromiseTest.prototype.testGetNameReturnsEmptyStringByDefault = function() {
	assertEquals("", this.testObj.getName());
};

PlayerNamePromiseTest.prototype.testGetNameReturnsExpectedValueAfterSetNameIsCalled = function() {
	var expectedName = "Randy Foobar";
	this.testObj.setName(expectedName);
	assertEquals(expectedName, this.testObj.getName());
};

PlayerNamePromiseTest.prototype.testSetNameUpdatesRegisteredElements = function() {
	var element1 = mock(TEST.FakeJQueryElement);
	var element2 = mock(TEST.FakeJQueryElement);

	this.testObj.registerForUpdates(element1);
	this.testObj.registerForUpdates(element2);

	var expectedName = "George Bingbaz";
	this.testObj.setName(expectedName);

	verify(element1).text(expectedName);
};

PlayerNamePromiseTest.prototype.testRegisterForUpdatesUpdatesElementIfAlreadyHasName = function() {
	var element = mock(TEST.FakeJQueryElement);
	var expectedName = "Jimmy Droptables";

	this.testObj.setName(expectedName);
	this.testObj.registerForUpdates(element);

	verify(element).text(expectedName);	
};

PlayerNamePromiseTest.prototype.testRegisterForUpdatesDoesNotUpdateElementIfDoesNotHaveName = function() {
	var element = mock(TEST.FakeJQueryElement);

	this.testObj.registerForUpdates(element);

	verify(element, never()).text(anything());
};