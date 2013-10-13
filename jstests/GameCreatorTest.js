GameCreatorTest = TestCase("GameCreatorTest")

GameCreatorTest.prototype.setUp = function() {
	this.playerId = "12345";
	this.ajax = mock(AVOCADO.Ajax);
	this.button = mock(TEST.FakeJQueryElement);
	this.viewManager = mock(AVOCADO.ViewManager);
	this.buildTestObj();
};

GameCreatorTest.prototype.testCreateGameCallsServerWithCorrectData = function() {
	var params = null;
	when(this.ajax).call("createGame", anything(), anything()).then(function(action, data, callback) {
		params = data;
	});
	this.testObj.createGame();
	assertEquals(this.playerId, params["playerId"]);
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
	verify(this.viewManager).showView("gameList");
};

GameCreatorTest.prototype.testUnsuccessfullCreateGameResponseDoesNotRefreshesGameListView = function() {
	this.ajax = new TEST.FakeAjax();
	this.ajax.callbackResponse = {"success" : false};
	this.buildTestObj();

	this.testObj.createGame();
	verify(this.viewManager, never()).showView("gameList");
};

GameCreatorTest.prototype.buildTestObj = function() {
	this.testObj = AVOCADO.GameCreator.getInstance(this.playerId, this.ajax, this.button, this.viewManager);
};
