GameCreatorTest = TestCase("GameCreatorTest")

GameCreatorTest.prototype.setUp = function() {
	this.fbId = "12345";
	this.ajax = mock(AVOCADO.Ajax);
	this.button = mock(TEST.FakeJQueryElement);
	this.gameListView = mock(AVOCADO.GameListView);
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

GameCreatorTest.prototype.testSuccessfullCreateGameResponseRefreshesGameListView = function() {
	this.ajax = new TEST.FakeAjax();
	this.ajax.callbackResponse = {"success" : true};
	this.buildTestObj();

	this.testObj.createGame();
	verify(this.gameListView).show();
};

GameCreatorTest.prototype.testUnsuccessfullCreateGameResponseDoesNotRefreshesGameListView = function() {
	this.ajax = new TEST.FakeAjax();
	this.ajax.callbackResponse = {"success" : false};
	this.buildTestObj();

	this.testObj.createGame();
	verify(this.gameListView, never()).show();
};

GameCreatorTest.prototype.buildTestObj = function() {
	this.testObj = AVOCADO.GameCreator.getInstance(this.fbId, this.ajax, this.button, this.gameListView);
};
