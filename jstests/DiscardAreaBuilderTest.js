DiscardAreaBuilderTest = TestCase("DiscardAreaBuilderTest");

DiscardAreaBuilderTest.prototype.setUp = function() {
	this.playerId = "123456";
	this.currentPlayerId = this.playerId;
	this.gameId = 908234;
	this.templateRenderer = mock(AVOCADO.TemplateRenderer);
	this.jqueryWrapper = mock(AVOCADO.JQueryWrapper);
	this.locStrings = {"discardMessage" : "discard some cards, fool!"};

	this.status = "discard";

	this.discardHtml = "some HTML for discarding";
	this.trainAreaTemplate(this.leaderHtml);

	this.discardElement = mock(TEST.FakeJQueryElement);
	when(this.jqueryWrapper).getElement(this.discardHtml).thenReturn(this.discardElement);

	this.cardElements = mock(TEST.FakeJQueryElement);

	this.ajax = mock(AVOCADO.Ajax);

	this.viewManager = mock(AVOCADO.ViewManager);

	this.buildTestObj();
};

DiscardAreaBuilderTest.prototype.testReturnsExpectedJQueryElement = function() {
	var actualResult = this.trigger();
	assertEquals(this.discardElement, actualResult);
};

DiscardAreaBuilderTest.prototype.testReturnsNullWhenStatusIsNotDiscard = function() {
	this.status = "trump_selection";
	
	var actualResult = this.trigger();
	assertEquals(null, actualResult);
};

DiscardAreaBuilderTest.prototype.testAddsClickHandlersAndClassToCardImages = function() {
	var cardClickHandler = function() {};
	this.testObj.buildCardClickHandler = mockFunction();
	when(this.testObj.buildCardClickHandler)(this.gameId).thenReturn(cardClickHandler);

	this.trigger();

	verify(this.cardElements).addClass("clickableCard");
	verify(this.cardElements).click(cardClickHandler);
};

DiscardAreaBuilderTest.prototype.testHandleCardClickCallsAjaxCorrectly = function() {
	var refreshViewFunc = function() {};
	this.testObj.buildRefreshViewFunc = mockFunction();
	when(this.testObj.buildRefreshViewFunc)(this.gameId).thenReturn(refreshViewFunc);

	var suit = Math.floor(Math.random() * 4) + 1;
	var value = Math.floor(Math.random() * 5) + 9;
	var cardHtml = "foo bar card html!";
	var cardElement = mock(TEST.FakeJQueryElement);
	var suitElement = mock(TEST.FakeJQueryElement);
	var valueElement = mock(TEST.FakeJQueryElement);
	when(this.jqueryWrapper).getElement(cardHtml).thenReturn(cardElement);
	when(cardElement).find(".cardSuit").thenReturn(suitElement);
	when(cardElement).find(".cardValue").thenReturn(valueElement);
	when(suitElement).val().thenReturn(suit);
	when(valueElement).val().thenReturn(value);
	var event = {"currentTarget" : cardHtml};

	this.testObj.buildCardClickHandler(this.gameId)(event);

	verify(this.ajax).call("discard", allOf(
		hasMember("playerId", this.playerId),
		hasMember("gameId", this.gameId),
		hasMember("suit", suit),
		hasMember("value", value)
	), refreshViewFunc);
};

DiscardAreaBuilderTest.prototype.testRefreshViewFuncCallsViewManagerCorrectly = function() {
	this.testObj.buildRefreshViewFunc(this.gameId)();
	verify(this.viewManager).showView("gamePlay", allOf(hasMember("gameId", this.gameId), hasMember("playerId", this.playerId)));
};

DiscardAreaBuilderTest.prototype.testDoesNotBindClickHandlersIfNotCurrentPlayersTurn = function() {
	this.currentPlayerId = "7890123";
	this.trigger();
	verify(this.cardElements, never()).addClass("clickableCard");
	verify(this.cardElements, never()).click(func());
};

DiscardAreaBuilderTest.prototype.buildTestObj = function() {
	this.testObj = AVOCADO.DiscardAreaBuilder.getInstance(this.templateRenderer, this.jqueryWrapper, this.locStrings, this.ajax, this.playerId, this.viewManager);
};

DiscardAreaBuilderTest.prototype.trigger = function() {
	return this.testObj.buildDiscardArea(this.status, this.cardElements, this.gameId, this.currentPlayerId);
};

DiscardAreaBuilderTest.prototype.trainAreaTemplate = function(expectedLeaderHtml) {
	when(this.templateRenderer).renderTemplate("discard", allOf(
		hasMember("discardMessage", this.locStrings.discardMessage)
	)).thenReturn(this.discardHtml);
};
