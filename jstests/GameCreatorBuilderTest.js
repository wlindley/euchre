GameCreatorBuilderTest = TestCase("GameCreatorBuilderTest")

GameCreatorBuilderTest.prototype.setUp = function() {
	this.playerId = "12345";
	this.requestTitle = "title";
	this.requestMessage = "message";

	this.ajax = mock(AVOCADO.Ajax);
	this.viewManager = mock(AVOCADO.ViewManager);
	this.templateRenderer = mock(AVOCADO.TemplateRenderer);
	this.jqueryWrapper = mock(AVOCADO.JQueryWrapper);
	this.facebook = mock(AVOCADO.Facebook);
	this.locStrings = {
		"gameInviteTitle" : this.requestTitle,
		"gameInviteMessage" : this.requestMessage
	};

	when(this.facebook).getSignedInPlayerId().thenReturn(this.playerId);

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

GameCreatorBuilderTest.prototype.tearDown = function() {
	setTimeout = this.origSetTimeout;
};

GameCreatorBuilderTest.prototype.testBuildGameCreatorReturnsExpectedElement = function() {
	var element = this.trigger();
	assertEquals(this.gameCreatorElement, element);
};

GameCreatorBuilderTest.prototype.testBuildGameCreatorAttachesClickHandler = function() {
	this.trigger();

	verify(this.createGameButton).click(this.testObj.createGameClickHandler);
};

GameCreatorBuilderTest.prototype.testCreateGameCallsServerWithCorrectData = function() {
	var params = null;
	when(this.ajax).call("createGame", anything(), anything()).then(function(action, data, callback) {
		params = data;
	});
	this.testObj.createGameClickHandler();
	assertEquals(this.playerId, params["playerId"]);
	assertEquals(0, params["team"]);
};

GameCreatorBuilderTest.prototype.testSuccessfullCreateGameResponseRefreshesGameListViewAndTriggersFBRequestSend = function() {
	var testHarness = this;
	var hasCalledAsync = false;
	setTimeout = function(func, time, lang) {
		verify(testHarness.viewManager, never()).showView("gameList");
		func();
		hasCalledAsync = true;
		verify(testHarness.viewManager).showView("gameList");
	};
	var gameId = "20394lskajd";

	this.ajax = new TEST.FakeAjax();
	this.ajax.callbackResponse = {"success" : true, "gameId" : gameId};
	this.buildTestObj();

	this.testObj.createGameClickHandler();
	assertTrue(hasCalledAsync);
	verify(this.facebook).sendRequests(this.requestTitle, this.requestMessage, hasMember("gameId", gameId));
};

GameCreatorBuilderTest.prototype.testUnsuccessfullCreateGameResponseDoesNotRefreshesGameListView = function() {
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

GameCreatorBuilderTest.prototype.doTraining = function() {
	when(this.templateRenderer).renderTemplate("gameCreator").thenReturn(this.gameCreatorHtml);
	when(this.jqueryWrapper).getElement(this.gameCreatorHtml).thenReturn(this.gameCreatorElement);
	when(this.gameCreatorElement).find("#btnCreateGame").thenReturn(this.createGameButton);
};

GameCreatorBuilderTest.prototype.trigger = function() {
	return this.testObj.buildGameCreator();
};

GameCreatorBuilderTest.prototype.buildTestObj = function() {
	this.testObj = AVOCADO.GameCreatorBuilder.getInstance(this.facebook, this.ajax, this.viewManager, this.templateRenderer, this.jqueryWrapper, this.locStrings);
};
