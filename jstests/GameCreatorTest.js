GameCreatorTest = TestCase("GameCreatorTest")

GameCreatorTest.prototype.setUp = function() {
	this.playerId = "12345";
	this.ajax = mock(AVOCADO.Ajax);
	this.viewManager = mock(AVOCADO.ViewManager);
	this.templateRenderer = mock(AVOCADO.TemplateRenderer);
	this.jqueryWrapper = mock(AVOCADO.JQueryWrapper);
	this.origSetTimeout = setTimeout;
	this.origSetTimeout = function(func, time, lang) {
		func();
	};

	this.gameCreatorHtml = "game creator";
	this.gameCreatorElement = mock(TEST.FakeJQueryElement);
	this.createGameButton = mock(TEST.FakeJQueryElement);

	this.buildTestObj();
	this.doTraining();
};

GameCreatorTest.prototype.tearDown = function() {
	setTimeout = this.origSetTimeout;
};

GameCreatorTest.prototype.testBuildGameCreatorReturnsExpectedElement = function() {
	var element = this.trigger();
	assertEquals(this.gameCreatorElement, element);
};

GameCreatorTest.prototype.testBuildGameCreatorAttachesClickHandler = function() {
	this.trigger();

	verify(this.createGameButton).click(this.testObj.createGameClickHandler);
};

GameCreatorTest.prototype.testCreateGameCallsServerWithCorrectData = function() {
	var params = null;
	when(this.ajax).call("createGame", anything(), anything()).then(function(action, data, callback) {
		params = data;
	});
	this.testObj.createGameClickHandler();
	assertEquals(this.playerId, params["playerId"]);
	assertEquals(0, params["team"]);
};

GameCreatorTest.prototype.testSuccessfullCreateGameResponseRefreshesGameListView = function() {
	var testHarness = this;
	var hasCalledAsync = false;
	setTimeout = function(func, time, lang) {
		verify(testHarness.viewManager, never()).showView("gameList");
		func();
		hasCalledAsync = true;
		verify(testHarness.viewManager).showView("gameList");
	};

	this.ajax = new TEST.FakeAjax();
	this.ajax.callbackResponse = {"success" : true};
	this.buildTestObj();

	this.testObj.createGameClickHandler();
	assertTrue(hasCalledAsync);
};

GameCreatorTest.prototype.testUnsuccessfullCreateGameResponseDoesNotRefreshesGameListView = function() {
	var hasCalledAsync = false;
	setTimeout = function(func, time, lang) {
		hasCalledAsync = true;
		func();
	};

	this.ajax = new TEST.FakeAjax();
	this.ajax.callbackResponse = {"success" : false};
	this.buildTestObj();

	this.testObj.createGameClickHandler();
	verify(this.viewManager, never()).showView("gameList");
	assertFalse(hasCalledAsync);
};

GameCreatorTest.prototype.doTraining = function() {
	when(this.templateRenderer).renderTemplate("gameCreator").thenReturn(this.gameCreatorHtml);
	when(this.jqueryWrapper).getElement(this.gameCreatorHtml).thenReturn(this.gameCreatorElement);
	when(this.gameCreatorElement).find("#btnCreateGame").thenReturn(this.createGameButton);
};

GameCreatorTest.prototype.trigger = function() {
	return this.testObj.buildGameCreator();
};

GameCreatorTest.prototype.buildTestObj = function() {
	this.testObj = AVOCADO.GameCreator.getInstance(this.playerId, this.ajax, this.viewManager, this.templateRenderer, this.jqueryWrapper);
};
