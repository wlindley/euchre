TrumpSelectionAreaBuilder = TestCase("TrumpSelectionAreaBuilder");

TrumpSelectionAreaBuilder.prototype.setUp = function() {
	this.locStrings = {"player" : "player %playerId%"};
	this.playerId = "030480983";
	this.currentPlayerId = this.playerId;
	this.gameId = 34987234;
	this.dealerId = "092380213";
	this.dealerName = this.locStrings["player"].replace("%playerId%", this.dealerId);
	this.status = "trump_selection";

	this.templateRenderer = mock(AVOCADO.TemplateRenderer);

	this.upCard = {"suit" : 1, "value" : 10};
	this.upCardHtml = "up card html";

	this.trumpSelection1ActionHtml = "trump 1 action";
	when(this.templateRenderer).renderTemplate("trumpSelection1Action", anything()).thenReturn(this.trumpSelection1ActionHtml);
	this.trumpSelection2ActionHtml = "trump 2 action";
	when(this.templateRenderer).renderTemplate("trumpSelection2Action", anything()).thenReturn(this.trumpSelection2ActionHtml);

	this.jqueryWrapper = mock(AVOCADO.JQueryWrapper);

	this.trumpSelectionElement = mock(TEST.FakeJQueryElement);
	this.passButtonElement = mock(TEST.FakeJQueryElement);
	when(this.trumpSelectionElement).find(".trumpSelectionPassButton").thenReturn(this.passButtonElement);
	this.dealerPicksUpButtonElement = mock(TEST.FakeJQueryElement);
	when(this.trumpSelectionElement).find(".dealerPicksUpButton").thenReturn(this.dealerPicksUpButtonElement);
	this.selectTrumpSuitButtonElement = mock(TEST.FakeJQueryElement);
	when(this.trumpSelectionElement).find(".selectTrumpSuitButton").thenReturn(this.selectTrumpSuitButtonElement);
	this.selectTrumpSuitInputElement = mock(TEST.FakeJQueryElement);
	when(this.trumpSelectionElement).find(".selectTrumpSuitInput").thenReturn(this.selectTrumpSuitInputElement);

	this.ajax = mock(AVOCADO.Ajax);

	this.viewManager = mock(AVOCADO.ViewManager);

	this.buildTestObj();

	this.refreshDisplayFunc = function() {};
	this.testObj.buildRefreshViewFunc = mockFunction();
	when(this.testObj.buildRefreshViewFunc)(this.gameId).thenReturn(this.refreshDisplayFunc);
};

TrumpSelectionAreaBuilder.prototype.testBuildReturnsExpectedResultWhenGivenValidData = function() {
	this.train(this.trumpSelection1ActionHtml);

	var passClickHandler = function() {};
	this.testObj.buildPassClickHandler = mockFunction();
	when(this.testObj.buildPassClickHandler)(this.gameId).thenReturn(passClickHandler);

	var dealerPicksUpClickHandler = function() {};
	this.testObj.buildDealerPicksUpClickHandler = mockFunction();
	when(this.testObj.buildDealerPicksUpClickHandler)(this.gameId, this.upCard.suit).thenReturn(dealerPicksUpClickHandler);

	assertEquals(this.trumpSelectionElement, this.testObj.buildTrumpSelectionArea(this.upCard, this.status, this.gameId, this.dealerId, this.currentPlayerId));

	verify(this.passButtonElement).click(passClickHandler);
	verify(this.dealerPicksUpButtonElement).click(dealerPicksUpClickHandler);
};

TrumpSelectionAreaBuilder.prototype.testBuildReturnsExpectedResultWhenGivenValidDataAndStatusIsTrumpSelection2 = function() {
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

	assertEquals(this.trumpSelectionElement, this.testObj.buildTrumpSelectionArea(null, this.status, this.gameId, this.dealerId, this.currentPlayerId));

	verify(this.passButtonElement).click(passClickHandler);
	verify(this.selectTrumpSuitButtonElement).click(selectTrumpSuitClickHandler);
};

TrumpSelectionAreaBuilder.prototype.testBuildReturnsExpectedResultWhenGivenValidDataAndStatusIsTrumpSelection2AndNotPlayersTurn = function() {
	this.currentPlayerId = this.playerId + "4325";
	this.templateRenderer = mock(AVOCADO.TemplateRenderer);
	when(this.templateRenderer).renderTemplate("card", allOf(hasMember("suit", 0), hasMember("value", 0))).thenReturn(this.upCardHtml);
	when(this.templateRenderer).renderTemplate("trumpSelection1Action", anything()).thenReturn(this.trumpSelection1ActionHtml);
	when(this.templateRenderer).renderTemplate("trumpSelection2Action", anything()).thenReturn(this.trumpSelection2ActionHtml);

	this.buildTestObj();
	this.status = "trump_selection_2";
	this.train("");

	assertEquals(this.trumpSelectionElement, this.testObj.buildTrumpSelectionArea(null, this.status, this.gameId, this.dealerId, this.currentPlayerId));
};

TrumpSelectionAreaBuilder.prototype.testBuildDoesNotIncludeActionsWhenNotCurrentPlayersTurn = function() {
	this.currentPlayerId = this.playerId + "4325";
	this.templateRenderer = mock(AVOCADO.TemplateRenderer);
	this.buildTestObj();
	when(this.templateRenderer).renderTemplate("card", allOf(hasMember("suit", this.upCard.suit), hasMember("value", this.upCard.value))).thenReturn(this.upCardHtml);
	when(this.templateRenderer).renderTemplate("trumpSelection1Action", anything()).thenReturn(this.trumpSelection1ActionHtml);
	when(this.templateRenderer).renderTemplate("trumpSelection2Action", anything()).thenReturn(this.trumpSelection2ActionHtml);
	this.train("");

	assertEquals(this.trumpSelectionElement, this.testObj.buildTrumpSelectionArea(this.upCard, this.status, this.gameId, this.dealerId, this.currentPlayerId));

	verify(this.templateRenderer, never()).renderTemplate("trumpSelection1Action", anything());
	verify(this.passButtonElement, never()).click(func());
	verify(this.passButtonElement).hide();
	verify(this.dealerPicksUpButtonElement, never()).click(func());
};

TrumpSelectionAreaBuilder.prototype.testBuildDoesNotIncludeActionsWhenNotCurrentPlayersTurnAndInTrumpSelection2 = function() {
	this.currentPlayerId = this.playerId + "4325";
	this.status = "trump_selection_2";
	this.templateRenderer = mock(AVOCADO.TemplateRenderer);
	this.buildTestObj();
	when(this.templateRenderer).renderTemplate("card", allOf(hasMember("suit", this.upCard.suit), hasMember("value", this.upCard.value))).thenReturn(this.upCardHtml);
	when(this.templateRenderer).renderTemplate("trumpSelection1Action", anything()).thenReturn(this.trumpSelection1ActionHtml);
	when(this.templateRenderer).renderTemplate("trumpSelection2Action", anything()).thenReturn(this.trumpSelection2ActionHtml);
	this.train("");

	assertEquals(this.trumpSelectionElement, this.testObj.buildTrumpSelectionArea(this.upCard, this.status, this.gameId, this.dealerId, this.currentPlayerId));

	verify(this.templateRenderer, never()).renderTemplate("trumpSelection1Action", anything());
	verify(this.passButtonElement, never()).click(func());
	verify(this.passButtonElement).hide();
	verify(this.dealerPicksUpButtonElement, never()).click(func());
};


TrumpSelectionAreaBuilder.prototype.testBuildReturnsNullWhenStatusIsRoundInProgress = function() {
	this.status = "round_in_progress";
	assertEquals(null, this.testObj.buildTrumpSelectionArea(this.upCard, this.status, this.gameId, this.dealerId));
};

TrumpSelectionAreaBuilder.prototype.testHandlePassClickedCallsAjaxWithCorrectData = function() {
	this.testObj.buildPassClickHandler(this.gameId)(null);
	verify(this.ajax).call("selectTrump", allOf(hasMember("suit", 0), hasMember("playerId", this.playerId), hasMember("gameId", this.gameId)), this.refreshDisplayFunc);
};

TrumpSelectionAreaBuilder.prototype.testHandleDealerPicksUpClickedCallsAjaxWithCorrectData = function() {
	this.testObj.buildDealerPicksUpClickHandler(this.gameId, this.upCard.suit)(null);
	verify(this.ajax).call("selectTrump", allOf(hasMember("suit", this.upCard.suit), hasMember("playerId", this.playerId), hasMember("gameId", this.gameId)), this.refreshDisplayFunc);
};

TrumpSelectionAreaBuilder.prototype.testHandleSelectTrumpSuitClickedCallsAjaxWithCorrectData = function() {
	var possibleSuits = ["Hearts", "SpAdes", "dIAmOndS", "ClubS"];
	var intValues = [4, 3, 2, 1];
	var index = Math.floor(Math.random() * possibleSuits.length);
	var selectedSuit = possibleSuits[index];
	var selectedValue = intValues[index];
	when(this.selectTrumpSuitInputElement).val().thenReturn(selectedSuit);

	this.testObj.buildSelectTrumpSuitClickHandler(this.gameId, this.selectTrumpSuitInputElement)(null);
	verify(this.ajax).call("selectTrump", allOf(hasMember("suit", selectedValue), hasMember("playerId", this.playerId), hasMember("gameId", this.gameId)), this.refreshDisplayFunc);
};

TrumpSelectionAreaBuilder.prototype.testRefreshViewFuncCallsViewManager = function() {
	this.buildTestObj();
	this.testObj.buildRefreshViewFunc(this.gameId)(null);
	verify(this.viewManager).showView("gamePlay", allOf(hasMember("gameId", this.gameId), hasMember("playerId", this.playerId)));
};

TrumpSelectionAreaBuilder.prototype.train = function(trumpSelectionActionHtml) {
	this.trumpSelectionHtml = "trump selection section";
	when(this.templateRenderer).renderTemplate("trumpSelection", allOf(hasMember("card", this.upCardHtml), hasMember("dealerName", this.dealerName), hasMember("trumpSelectionAction", trumpSelectionActionHtml))).thenReturn(this.trumpSelectionHtml);
	when(this.jqueryWrapper).getElement(this.trumpSelectionHtml).thenReturn(this.trumpSelectionElement);

	if (null != this.upCard) {
		when(this.templateRenderer).renderTemplate("card", allOf(hasMember("suit", this.upCard.suit), hasMember("value", this.upCard.value))).thenReturn(this.upCardHtml);
	} else {
		when(this.templateRenderer).renderTemplate("card", allOf(hasMember("suit", 0), hasMember("value", 0))).thenReturn(this.upCardHtml);
	}
};

TrumpSelectionAreaBuilder.prototype.buildTestObj = function() {
	this.testObj = new AVOCADO.TrumpSelectionAreaBuilder(this.templateRenderer, this.jqueryWrapper, this.ajax, this.playerId, this.locStrings, this.viewManager);
};
