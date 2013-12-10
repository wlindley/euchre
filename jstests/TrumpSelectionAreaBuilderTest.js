TrumpSelectionAreaBuilderTest = TestCase("TrumpSelectionAreaBuilderTest");

TrumpSelectionAreaBuilderTest.prototype.setUp = function() {
	this.locStrings = {"yourTeam" : "your team", "otherTeam" : "other team"};
	this.playerId = "030480983";
	this.currentPlayerId = this.playerId;
	this.gameId = 34987234;
	this.dealerId = "092380213";
	this.status = "trump_selection";
	this.teams = [[this.playerId, this.dealerId], ["3", "4"]];
	this.dealerTeamString = this.locStrings.yourTeam;

	this.templateRenderer = mock(AVOCADO.TemplateRenderer);

	this.playerNameDirectory = mock(AVOCADO.PlayerNameDirectory);
	this.dealerNamePromise = mock(AVOCADO.PlayerNamePromise);
	when(this.playerNameDirectory).getNamePromise(this.dealerId).thenReturn(this.dealerNamePromise);

	this.upCard = {"suit" : 1, "value" : 10};
	this.upCardHtml = "up card html";

	this.trumpSelection1ActionHtml = "trump 1 action";
	when(this.templateRenderer).renderTemplate("trumpSelection1Action", anything()).thenReturn(this.trumpSelection1ActionHtml);
	this.trumpSelection2ActionHtml = "trump 2 action";
	when(this.templateRenderer).renderTemplate("trumpSelection2Action", anything()).thenReturn(this.trumpSelection2ActionHtml);

	this.jqueryWrapper = mock(AVOCADO.JQueryWrapper);
	this.facebook = mock(AVOCADO.Facebook);
	when(this.facebook).getSignedInPlayerId().thenReturn(this.playerId);

	this.trumpSelectionElement = mock(TEST.FakeJQueryElement);
	this.passButtonElement = mock(TEST.FakeJQueryElement);
	when(this.trumpSelectionElement).find(".trumpSelectionPassButton").thenReturn(this.passButtonElement);
	this.dealerPicksUpButtonElement = mock(TEST.FakeJQueryElement);
	when(this.trumpSelectionElement).find(".dealerPicksUpButton").thenReturn(this.dealerPicksUpButtonElement);
	this.selectTrumpSuitButtonElement = mock(TEST.FakeJQueryElement);
	when(this.trumpSelectionElement).find(".selectTrumpSuitButton").thenReturn(this.selectTrumpSuitButtonElement);
	this.selectTrumpSuitInputElement = mock(TEST.FakeJQueryElement);
	when(this.trumpSelectionElement).find(".selectTrumpSuitInput").thenReturn(this.selectTrumpSuitInputElement);
	this.dealerElement = mock(TEST.FakeJQueryElement);
	when(this.trumpSelectionElement).find(".dealer").thenReturn(this.dealerElement);
	this.dealerNameElement = mock(TEST.FakeJQueryElement);
	when(this.dealerElement).find(".playerName").thenReturn(this.dealerNameElement);
	this.dealerLabelElement = mock(TEST.FakeJQueryElement);
	when(this.dealerElement).find(".label").thenReturn(this.dealerLabelElement);
	this.suitDropdownElement = mock(TEST.FakeJQueryElement);
	when(this.trumpSelectionElement).find(".ui.dropdown").thenReturn(this.suitDropdownElement);
	this.trumpSelectionActionsElement = mock(TEST.FakeJQueryElement);
	when(this.trumpSelectionElement).find(".trumpSelectionActions").thenReturn(this.trumpSelectionActionsElement);

	this.ajax = mock(AVOCADO.Ajax);
	this.ajaxPromise = mock(TEST.FakePromise);

	this.viewManager = mock(AVOCADO.ViewManager);

	this.origSetTimeout = setTimeout;
	setTimeout = function(func, time, lang) {
		func();
	};

	this.buildTestObj();

	this.refreshDisplayFunc = function() {};
	this.testObj.buildRefreshViewFunc = mockFunction();
	when(this.testObj.buildRefreshViewFunc)(this.gameId).thenReturn(this.refreshDisplayFunc);
};

TrumpSelectionAreaBuilderTest.prototype.tearDown = function() {
	setTimeout = this.origSetTimeout;
};

TrumpSelectionAreaBuilderTest.prototype.buildTestObj = function() {
	this.testObj = new AVOCADO.TrumpSelectionAreaBuilder(this.templateRenderer, this.jqueryWrapper, this.ajax, this.facebook, this.locStrings, this.viewManager, this.playerNameDirectory);
};

TrumpSelectionAreaBuilderTest.prototype.train = function(trumpSelectionActionHtml) {
	this.trumpSelectionHtml = "trump selection section";
	when(this.templateRenderer).renderTemplate("trumpSelection", allOf(hasMember("card", this.upCardHtml), hasMember("dealerTeam", this.dealerTeamString), hasMember("trumpSelectionAction", trumpSelectionActionHtml))).thenReturn(this.trumpSelectionHtml);
	when(this.jqueryWrapper).getElement(this.trumpSelectionHtml).thenReturn(this.trumpSelectionElement);

	if (null != this.upCard) {
		when(this.templateRenderer).renderTemplate("card", allOf(hasMember("suit", this.upCard.suit), hasMember("value", this.upCard.value))).thenReturn(this.upCardHtml);
	} else {
		when(this.templateRenderer).renderTemplate("card", allOf(hasMember("suit", 0), hasMember("value", 0))).thenReturn(this.upCardHtml);
	}
};

TrumpSelectionAreaBuilderTest.prototype.trigger = function(upCard) {
	return this.testObj.buildTrumpSelectionArea(upCard, this.status, this.gameId, this.dealerId, this.currentPlayerId, this.teams);
};

TrumpSelectionAreaBuilderTest.prototype.testBuildReturnsExpectedResultWhenGivenValidData = function() {
	this.train(this.trumpSelection1ActionHtml);

	var passClickHandler = function() {};
	this.testObj.buildPassClickHandler = mockFunction();
	when(this.testObj.buildPassClickHandler)(this.gameId).thenReturn(passClickHandler);

	var dealerPicksUpClickHandler = function() {};
	this.testObj.buildDealerPicksUpClickHandler = mockFunction();
	when(this.testObj.buildDealerPicksUpClickHandler)(this.gameId, this.upCard.suit).thenReturn(dealerPicksUpClickHandler);

	assertEquals(this.trumpSelectionElement, this.trigger(this.upCard));

	verify(this.passButtonElement).click(passClickHandler);
	verify(this.dealerPicksUpButtonElement).click(dealerPicksUpClickHandler);
	verify(this.suitDropdownElement).dropdown();
	verify(this.dealerLabelElement).addClass("green");
};

TrumpSelectionAreaBuilderTest.prototype.testBuildReturnsExpectedResultWhenDealerIsOnOtherTeam = function() {
	this.teams = [[this.playerId, "2"], [this.dealerId, "3"]];
	this.dealerTeamString = this.locStrings.otherTeam;
	this.train(this.trumpSelection1ActionHtml);

	assertEquals(this.trumpSelectionElement, this.trigger(this.upCard));
	verify(this.dealerLabelElement).addClass("red");
};

TrumpSelectionAreaBuilderTest.prototype.testBuildHooksUpDealerNamePromise = function() {
	this.train(this.trumpSelectionActionHtml);
	this.trigger(this.upCard);
	verify(this.dealerNamePromise).registerForUpdates(this.dealerNameElement);
};

TrumpSelectionAreaBuilderTest.prototype.testBuildReturnsExpectedResultWhenGivenValidDataAndStatusIsTrumpSelection2 = function() {
	this.templateRenderer = mock(AVOCADO.TemplateRenderer);
	when(this.templateRenderer).renderTemplate("card", allOf(hasMember("suit", 0), hasMember("value", 0))).thenReturn(this.upCardHtml);
	when(this.templateRenderer).renderTemplate("trumpSelection1Action", anything()).thenReturn(this.trumpSelection1ActionHtml);
	when(this.templateRenderer).renderTemplate("trumpSelection2Action", anything()).thenReturn(this.trumpSelection2ActionHtml);

	this.buildTestObj();
	this.status = "trump_selection_2";
	this.train(this.trumpSelection2ActionHtml);

	var passClickHandler = function() {};
	this.testObj.buildPassClickHandler = mockFunction();
	when(this.testObj.buildPassClickHandler)(this.gameId).thenReturn(passClickHandler);

	var selectTrumpSuitClickHandler = function() {};
	this.testObj.buildSelectTrumpSuitClickHandler = mockFunction();
	when(this.testObj.buildSelectTrumpSuitClickHandler)(this.gameId, this.selectTrumpSuitInputElement).thenReturn(selectTrumpSuitClickHandler);

	assertEquals(this.trumpSelectionElement, this.trigger(null));

	verify(this.passButtonElement).click(passClickHandler);
	verify(this.selectTrumpSuitButtonElement).click(selectTrumpSuitClickHandler);
};

TrumpSelectionAreaBuilderTest.prototype.testBuildReturnsExpectedResultWhenGivenValidDataAndStatusIsTrumpSelection2AndNotPlayersTurn = function() {
	this.currentPlayerId = this.playerId + "4325";
	this.templateRenderer = mock(AVOCADO.TemplateRenderer);
	when(this.templateRenderer).renderTemplate("card", allOf(hasMember("suit", 0), hasMember("value", 0))).thenReturn(this.upCardHtml);
	when(this.templateRenderer).renderTemplate("trumpSelection1Action", anything()).thenReturn(this.trumpSelection1ActionHtml);
	when(this.templateRenderer).renderTemplate("trumpSelection2Action", anything()).thenReturn(this.trumpSelection2ActionHtml);

	this.buildTestObj();
	this.status = "trump_selection_2";
	this.train("");

	assertEquals(this.trumpSelectionElement, this.trigger(null));
};

TrumpSelectionAreaBuilderTest.prototype.testBuildDoesNotIncludeActionsWhenNotCurrentPlayersTurn = function() {
	this.currentPlayerId = this.playerId + "4325";
	this.templateRenderer = mock(AVOCADO.TemplateRenderer);
	this.buildTestObj();
	when(this.templateRenderer).renderTemplate("card", allOf(hasMember("suit", this.upCard.suit), hasMember("value", this.upCard.value))).thenReturn(this.upCardHtml);
	when(this.templateRenderer).renderTemplate("trumpSelection1Action", anything()).thenReturn(this.trumpSelection1ActionHtml);
	when(this.templateRenderer).renderTemplate("trumpSelection2Action", anything()).thenReturn(this.trumpSelection2ActionHtml);
	this.train("");

	assertEquals(this.trumpSelectionElement, this.trigger(this.upCard));

	verify(this.templateRenderer, never()).renderTemplate("trumpSelection1Action", anything());
	verify(this.passButtonElement, never()).click(func());
	verify(this.dealerPicksUpButtonElement, never()).click(func());
	verify(this.trumpSelectionActionsElement).hide();
};

TrumpSelectionAreaBuilderTest.prototype.testBuildDoesNotIncludeActionsWhenNotCurrentPlayersTurnAndInTrumpSelection2 = function() {
	this.currentPlayerId = this.playerId + "4325";
	this.status = "trump_selection_2";
	this.templateRenderer = mock(AVOCADO.TemplateRenderer);
	this.buildTestObj();
	when(this.templateRenderer).renderTemplate("card", allOf(hasMember("suit", this.upCard.suit), hasMember("value", this.upCard.value))).thenReturn(this.upCardHtml);
	when(this.templateRenderer).renderTemplate("trumpSelection1Action", anything()).thenReturn(this.trumpSelection1ActionHtml);
	when(this.templateRenderer).renderTemplate("trumpSelection2Action", anything()).thenReturn(this.trumpSelection2ActionHtml);
	this.train("");

	assertEquals(this.trumpSelectionElement, this.trigger(this.upCard));

	verify(this.templateRenderer, never()).renderTemplate("trumpSelection1Action", anything());
	verify(this.passButtonElement, never()).click(func());
	verify(this.dealerPicksUpButtonElement, never()).click(func());
	verify(this.trumpSelectionActionsElement).hide();
};

TrumpSelectionAreaBuilderTest.prototype.testBuildReturnsNullWhenStatusIsRoundInProgress = function() {
	this.status = "round_in_progress";
	assertEquals(null, this.trigger(this.upCard));
};

TrumpSelectionAreaBuilderTest.prototype.testBuildReturnsNullWhenStatusIsDiscard = function() {
	this.status = "discard";
	assertEquals(null, this.trigger(this.upCard));
};

TrumpSelectionAreaBuilderTest.prototype.testHandlePassClickedCallsAjaxWithCorrectData = function() {
	var paramChecker = allOf(hasMember("suit", 0), hasMember("playerId", this.playerId), hasMember("gameId", this.gameId));
	when(this.ajax).call("selectTrump", paramChecker).thenReturn(this.ajaxPromise);
	this.testObj.buildPassClickHandler(this.gameId)(null);
	verify(this.ajax).call("selectTrump", paramChecker);
	verify(this.ajaxPromise).done(this.refreshDisplayFunc);
};

TrumpSelectionAreaBuilderTest.prototype.testHandleDealerPicksUpClickedCallsAjaxWithCorrectData = function() {
	var paramChecker = allOf(hasMember("suit", this.upCard.suit), hasMember("playerId", this.playerId), hasMember("gameId", this.gameId));
	when(this.ajax).call("selectTrump", paramChecker).thenReturn(this.ajaxPromise);
	this.testObj.buildDealerPicksUpClickHandler(this.gameId, this.upCard.suit)(null);
	verify(this.ajax).call("selectTrump", paramChecker);
	verify(this.ajaxPromise).done(this.refreshDisplayFunc);
};

TrumpSelectionAreaBuilderTest.prototype.testHandleSelectTrumpSuitClickedCallsAjaxWithCorrectData = function() {
	var possibleSuits = ["Hearts", "SpAdes", "dIAmOndS", "ClubS"];
	var intValues = [4, 3, 2, 1];
	var index = Math.floor(Math.random() * possibleSuits.length);
	var selectedSuit = possibleSuits[index];
	var selectedValue = intValues[index];

	var paramChecker = allOf(hasMember("suit", selectedValue), hasMember("playerId", this.playerId), hasMember("gameId", this.gameId))
	when(this.ajax).call("selectTrump", paramChecker).thenReturn(this.ajaxPromise);

	when(this.selectTrumpSuitInputElement).val().thenReturn(selectedSuit);

	this.testObj.buildSelectTrumpSuitClickHandler(this.gameId, this.selectTrumpSuitInputElement)(null);
	verify(this.ajax).call("selectTrump", paramChecker);
	verify(this.ajaxPromise).done(this.refreshDisplayFunc);
};

TrumpSelectionAreaBuilderTest.prototype.testRefreshViewFuncCallsViewManagerAfterDelay = function() {
	var testHarness = this;
	var hasCalledAsync = false;
	setTimeout = function(func, time, lang) {
		verify(testHarness.viewManager, never()).showView("gamePlay", allOf(hasMember("gameId", testHarness.gameId), hasMember("playerId", testHarness.playerId)));
		func();
		verify(testHarness.viewManager).showView("gamePlay", allOf(hasMember("gameId", testHarness.gameId), hasMember("playerId", testHarness.playerId)));
		hasCalledAsync = true;
	};
	this.buildTestObj();
	this.testObj.buildRefreshViewFunc(this.gameId)(null);
	assertTrue(hasCalledAsync);
};
