GameJoinerTest = TestCase("GameJoinerTest");

GameJoinerTest.prototype.setUp = function() {
	this.fbId = "1234567";
	this.ajax = mock(AVOCADO.Ajax);
	this.txtGameId = mock(TEST.FakeJQueryElement);
	this.txtTeamId = mock(TEST.FakeJQueryElement);
	this.btnJoinGame = mock(TEST.FakeJQueryElement);
	this.viewManager = mock(AVOCADO.ViewManager);
	this.templateRenderer = mock(AVOCADO.TemplateRenderer);
	this.jqueryWrapper = mock(AVOCADO.JQueryWrapper);
	this.origSetTimeout = setTimeout;
	setTimeout = function(func, time, lang) {
		func();
	};

	this.gameJoinerHtml = "game joiner";
	this.gameJoinerElement = mock(TEST.FakeJQueryElement);

	this.buildTestObj();
	this.doTraining();
};

GameJoinerTest.prototype.tearDown = function() {
	setTimeout = this.origSetTimeout;
};

GameJoinerTest.prototype.testBuildGameJoinerReturnsExpectedElement = function() {
	var result = this.trigger();
	assertEquals(this.gameJoinerElement, result);
};

GameJoinerTest.prototype.testBuildGameJoinerBindsClickHandler = function() {
	var clickHandler = function() {};
	var prevBuilderFunc = this.testObj.buildJoinGameClickHandler;
	this.testObj.buildJoinGameClickHandler = mockFunction();
	when(this.testObj.buildJoinGameClickHandler)(this.txtGameId, this.txtTeamId).thenReturn(clickHandler);

	this.trigger();
	verify(this.btnJoinGame).click(clickHandler);

	this.testObj.buildJoinGameClickHandler = prevBuilderFunc;
};

GameJoinerTest.prototype.testJoinGameFromTextFieldsCallsAjaxWithCorrectData = function() {
	var gameId = "1384";
	var teamId = "1";
	when(this.txtGameId).val().thenReturn(gameId);
	when(this.txtTeamId).val().thenReturn(teamId);

	this.testObj.buildJoinGameClickHandler(this.txtGameId, this.txtTeamId)();

	verify(this.ajax).call("addPlayer", allOf(hasMember("gameId", gameId), hasMember("team", teamId), hasMember("playerId", this.fbId)), func());
};

GameJoinerTest.prototype.testSuccessfulJoinGameResponseRefreshesGameListView = function() {
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

	this.testObj.buildJoinGameClickHandler(this.txtGameId, this.txtTeamId)();

	assertTrue(hasCalledAsync);
};

GameJoinerTest.prototype.testUnsuccessfulJoinGameResponseDoesNotRefreshesGameListView = function() {
	var testHarness = this;
	var hasCalledAsync = false;
	setTimeout = function(func, time, lang) {
		hasCalledAsync = true;
		func();
	};

	this.ajax = new TEST.FakeAjax();
	this.ajax.callbackResponse = {"success" : false};
	this.buildTestObj();

	this.testObj.buildJoinGameClickHandler(this.txtGameId, this.txtTeamId)();

	verify(this.viewManager, never()).showView("gameList");
	assertFalse(hasCalledAsync);
};

GameJoinerTest.prototype.doTraining = function() {
	when(this.templateRenderer).renderTemplate("gameJoiner").thenReturn(this.gameJoinerHtml);
	when(this.jqueryWrapper).getElement(this.gameJoinerHtml).thenReturn(this.gameJoinerElement);
	when(this.gameJoinerElement).find("#btnJoinGame").thenReturn(this.btnJoinGame);
	when(this.gameJoinerElement).find("#txtGameId").thenReturn(this.txtGameId);
	when(this.gameJoinerElement).find("#txtTeam").thenReturn(this.txtTeamId);
};

GameJoinerTest.prototype.trigger = function() {
	return this.testObj.buildGameJoiner();
};

GameJoinerTest.prototype.buildTestObj = function() {
	this.testObj = new AVOCADO.GameJoiner(this.fbId, this.ajax, this.viewManager, this.templateRenderer, this.jqueryWrapper);
};
