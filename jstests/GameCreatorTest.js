GameCreatorTest = TestCase("GameCreatorTest")

GameCreatorTest.prototype.setUp = function() {
	this.fbId = "12345";
	this.ajax = mock(Ajax);
	this.button = mock(FakeJQueryElement);
	this.buildTestObj();
};

GameCreatorTest.prototype.testCreateGameCallsServerWithCorrectData = function() {
	var params = null;
	when(this.ajax).call("createGame", anything(), anything()).then(function(action, data, callback) {
		params = data;
	});
	this.testObj.createGame();
	assertEquals(this.fbId, params["playerId"]);
	assertEquals(0, params["team"]);
};

GameCreatorTest.prototype.testInitBindsButtonClickHandler = function() {
	this.testObj.init();
	verify(this.button).click(this.testObj.createGame);
};

GameCreatorTest.prototype.buildTestObj = function() {
	this.testObj = GameCreator.getInstance(this.fbId, this.ajax, this.button);
};
