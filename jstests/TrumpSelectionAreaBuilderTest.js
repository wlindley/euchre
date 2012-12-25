TrumpSelectionAreaBuilder = TestCase("TrumpSelectionAreaBuilder");

TrumpSelectionAreaBuilder.prototype.setUp = function() {
	this.locStrings = {"player" : "player %playerId%"};
	this.playerId = "030480983";
	this.gameId = 34987234;
	this.dealerId = "092380213";
	this.dealerName = this.locStrings["player"].replace("%playerId%", this.dealerId);

	this.templateRenderer = mock(AVOCADO.TemplateRenderer);

	this.upCard = {"suit" : 1, "value" : 10};
	this.upCardHtml = "up card html";
	when(this.templateRenderer).renderTemplate("card", allOf(hasMember("suit", this.upCard.suit), hasMember("value", this.upCard.value))).thenReturn(this.upCardHtml);

	this.trumpSelectionHtml = "trump selection section";
	when(this.templateRenderer).renderTemplate("trumpSelection", allOf(hasMember("card", this.upCardHtml), hasMember("dealerName", this.dealerName))).thenReturn(this.trumpSelectionHtml);

	this.status = "trump_selection";

	this.jqueryWrapper = mock(AVOCADO.JQueryWrapper);

	this.trumpSelectionElement = mock(TEST.FakeJQueryElement);
	this.passButtonElement = mock(TEST.FakeJQueryElement);
	when(this.jqueryWrapper).getElement(this.trumpSelectionHtml).thenReturn(this.trumpSelectionElement);
	when(this.trumpSelectionElement).find(".trumpSelectionPassButton").thenReturn(this.passButtonElement);

	this.ajax = mock(AVOCADO.Ajax);

	this.buildTestObj();
};

TrumpSelectionAreaBuilder.prototype.testBuildReturnsExpectedResultWhenGivenValidData = function() {
	var clickHandler = function() {};
	this.testObj.buildPassClickHandler = mockFunction();
	when(this.testObj.buildPassClickHandler)(this.gameId).thenReturn(clickHandler);
	assertEquals(this.trumpSelectionElement, this.testObj.buildTrumpSelectionArea(this.upCard, this.status, this.gameId, this.dealerId));
	verify(this.passButtonElement).click(clickHandler);
};

TrumpSelectionAreaBuilder.prototype.testBuildReturnsNullWhenUpCardIsNull = function() {
	this.upCard = null;
	assertEquals(null, this.testObj.buildTrumpSelectionArea(this.upCard, this.status, this.gameId, this.dealerId));
};

TrumpSelectionAreaBuilder.prototype.testBuildReturnsNullWhenStatusIsRoundInProgress = function() {
	this.status = "round_in_progress";
	assertEquals(null, this.testObj.buildTrumpSelectionArea(this.upCard, this.status, this.gameId, this.dealerId));
};

TrumpSelectionAreaBuilder.prototype.testHandlePassClickedCallsAjaxWithCorrectData = function() {
	this.testObj.buildPassClickHandler(this.gameId)(null);
	verify(this.ajax).call("selectTrump", allOf(hasMember("suit", null), hasMember("playerId", this.playerId), hasMember("gameId", this.gameId)), func());
};

TrumpSelectionAreaBuilder.prototype.buildTestObj = function() {
	this.testObj = new AVOCADO.TrumpSelectionAreaBuilder(this.templateRenderer, this.jqueryWrapper, this.ajax, this.playerId, this.locStrings);
};
