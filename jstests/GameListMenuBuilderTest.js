GameListMenuBuilderTest = TestCase("GameListMenuBuilderTest")

GameListMenuBuilderTest.prototype.setUp = function() {
	this.playerId = "12345";
	this.requestTitle = "title";
	this.requestMessage = "message";
	this.appInviteRequestTitle = "app invite title";
	this.appInviteRequestMessage = "app invite message";

	this.ajax = mock(AVOCADO.Ajax);
	this.viewManager = mock(AVOCADO.ViewManager);
	this.templateRenderer = mock(AVOCADO.TemplateRenderer);
	this.jqueryWrapper = mock(AVOCADO.JQueryWrapper);
	this.facebook = mock(AVOCADO.Facebook);
	this.locStrings = {
		"gameInviteTitle" : this.requestTitle,
		"gameInviteMessage" : this.requestMessage,
		"appInviteTitle" : this.appInviteRequestTitle,
		"appInviteMessage" : this.appInviteRequestMessage
	};

	when(this.facebook).getSignedInPlayerId().thenReturn(this.playerId);

	this.origSetTimeout = setTimeout;
	this.origSetTimeout = function(func, time, lang) {
		func();
	};

	this.createGameElement = mock(TEST.FakeJQueryElement);
	this.inviteElement = mock(TEST.FakeJQueryElement);
	this.findGameElement = mock(TEST.FakeJQueryElement);
	this.findGameStatusElement = mock(TEST.FakeJQueryElement);
	this.gameMenuElement = mock(TEST.FakeJQueryElement);
	this.gameMenuHtml = "game menu html";

	this.ajaxPromise = mock(TEST.FakePromise);

	this.buildTestObj();
	this.doTraining();
};

GameListMenuBuilderTest.prototype.tearDown = function() {
	setTimeout = this.origSetTimeout;
};

GameListMenuBuilderTest.prototype.testBuildGameMenuReturnsExpectedElement = function() {
	var element = this.trigger();
	assertEquals(this.gameMenuElement, element);
};

GameListMenuBuilderTest.prototype.testBuildGameMenuAttachesClickHandlers = function() {
	this.trigger();

	verify(this.createGameElement).click(this.testObj.createGameClickHandler);
	verify(this.inviteElement).click(this.testObj.appInviteClickHandler);
	verify(this.findGameElement).click(this.testObj.findGameClickHandler);
};

GameListMenuBuilderTest.prototype.testBuildGameMenuHidesFindGameStatus = function() {
	this.trigger();

	verify(this.findGameStatusElement).hide();
	verify(this.findGameElement, never()).hide();
};

GameListMenuBuilderTest.prototype.testCreateGameCallsServerWithCorrectData = function() {
	this.testObj.createGameClickHandler();

	verify(this.ajax).call("createGame", allOf(
		hasMember("team", 0)
	));
};

GameListMenuBuilderTest.prototype.testSuccessfullCreateGameResponseRefreshesGameListViewAndTriggersFBRequestSend = function() {
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
	this.buildTestObj();

	this.testObj.createGameClickHandler();
	this.ajax.resolveCall({"success" : true, "gameId" : gameId});

	assertTrue(hasCalledAsync);
	verify(this.facebook).sendRequests(this.requestTitle, this.requestMessage, hasMember("gameId", gameId));
};

GameListMenuBuilderTest.prototype.testUnsuccessfullCreateGameResponseDoesNotRefreshesGameListView = function() {
	var hasCalledAsync = false;
	setTimeout = function(func, time, lang) {
		hasCalledAsync = true;
		func();
	};

	this.ajax = new TEST.FakeAjax();
	this.buildTestObj();

	this.testObj.createGameClickHandler();
	this.ajax.resolveCall({"success" : false});

	verify(this.viewManager, never()).showView("gameList");
	assertFalse(hasCalledAsync);
};

GameListMenuBuilderTest.prototype.testAppInviteTriggersFBRequestSend = function() {
	this.testObj.appInviteClickHandler();
	verify(this.facebook).sendRequests(this.appInviteRequestTitle, this.appInviteRequestMessage, anything());
};

GameListMenuBuilderTest.prototype.testFindGameCallsServerWithCorrectData = function() {
	this.testObj.findGameClickHandler();

	verify(this.ajax).call("matchmake");
};

GameListMenuBuilderTest.prototype.testFindGameResponseRefreshesGameListView = function() {
	var testHarness = this;
	var hasCalledAsync = false;
	setTimeout = function(func, time, lang) {
		verify(testHarness.viewManager, never()).showView("gameList");
		func();
		hasCalledAsync = true;
		verify(testHarness.viewManager).showView("gameList");
	};

	this.ajax = new TEST.FakeAjax();
	this.buildTestObj();

	this.testObj.findGameClickHandler();
	this.ajax.resolveCall({"success" : true});

	assertTrue(hasCalledAsync);
};

GameListMenuBuilderTest.prototype.doTraining = function() {
	when(this.ajax).call(anything(), anything()).thenReturn(this.ajaxPromise);
	when(this.ajax).call(anything()).thenReturn(this.ajaxPromise);
	when(this.templateRenderer).renderTemplate("gameListMenu").thenReturn(this.gameMenuHtml);
	when(this.jqueryWrapper).getElement(this.gameMenuHtml).thenReturn(this.gameMenuElement);
	when(this.gameMenuElement).find(".createGameButton").thenReturn(this.createGameElement);
	when(this.gameMenuElement).find(".inviteButton").thenReturn(this.inviteElement);
	when(this.gameMenuElement).find(".findGameButton").thenReturn(this.findGameElement);
	when(this.gameMenuElement).find(".findGameStatus").thenReturn(this.findGameStatusElement);
};

GameListMenuBuilderTest.prototype.trigger = function() {
	return this.testObj.buildGameMenu();
};

GameListMenuBuilderTest.prototype.buildTestObj = function() {
	this.testObj = AVOCADO.GameListMenuBuilder.getInstance(this.facebook, this.ajax, this.viewManager, this.templateRenderer, this.jqueryWrapper, this.locStrings);
};
