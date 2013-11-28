DiscardAreaBuilderTest = TestCase("DiscardAreaBuilderTest");

DiscardAreaBuilderTest.prototype.setUp = function() {
	this.playerId = "123456";
	this.currentPlayerId = this.playerId;
	this.gameId = 908234;
	this.templateRenderer = mock(AVOCADO.TemplateRenderer);
	this.jqueryWrapper = mock(AVOCADO.JQueryWrapper);
	this.locStrings = {"discardMessage" : "discard some cards, fool!"};

	this.status = "discard";

	this.origSetTimeout = setTimeout;
	setTimeout = function(func, time, lang) {
		func();
	};

	this.discardHtml = "some HTML for discarding";
	this.trainAreaTemplate(this.leaderHtml);

	this.discardElement = mock(TEST.FakeJQueryElement);
	when(this.jqueryWrapper).getElement(this.discardHtml).thenReturn(this.discardElement);

	this.cardElements = mock(TEST.FakeJQueryElement);

	this.ajax = mock(AVOCADO.Ajax);

	this.viewManager = mock(AVOCADO.ViewManager);

	this.facebook = mock(AVOCADO.Facebook);
	when(this.facebook).getSignedInPlayerId().thenReturn(this.playerId);

	this.buildTestObj();
};

DiscardAreaBuilderTest.prototype.tearDown = function() {
	setTimeout = this.origSetTimeout;
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

DiscardAreaBuilderTest.prototype.testReturnsNullWhenNotCurrentPlayersTurn = function() {
	this.currentPlayerId = "7890123";
	
	var actualResult = this.trigger();
	assertEquals(null, actualResult);
};

DiscardAreaBuilderTest.prototype.testAddsClickHandlersAndClassToCardImages = function() {
	var cardClickHandler = function() {};
	this.testObj.buildCardClickHandler = mockFunction();
	when(this.testObj.buildCardClickHandler)(this.gameId).thenReturn(cardClickHandler);

	this.trigger();

	verify(this.cardElements).addClass("clickable");
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

DiscardAreaBuilderTest.prototype.testRefreshViewFuncCallsViewManagerCorrectlyAfterDelay = function() {
	var testHarness = this;
	var hasCalledAsync = false;
	setTimeout = function(func, time, lang) {
		verify(testHarness.viewManager, never()).showView("gamePlay", allOf(hasMember("gameId", testHarness.gameId), hasMember("playerId", testHarness.playerId)));
		func();
		verify(testHarness.viewManager).showView("gamePlay", allOf(hasMember("gameId", testHarness.gameId), hasMember("playerId", testHarness.playerId)));
		hasCalledAsync = true;
	};
	this.testObj.buildRefreshViewFunc(this.gameId)();
	assertTrue(hasCalledAsync);
};

DiscardAreaBuilderTest.prototype.testDoesNotBindClickHandlersIfNotCurrentPlayersTurn = function() {
	this.currentPlayerId = "7890123";
	this.trigger();
	verify(this.cardElements, never()).addClass("clickable");
	verify(this.cardElements, never()).click(func());
};

DiscardAreaBuilderTest.prototype.buildTestObj = function() {
	this.testObj = AVOCADO.DiscardAreaBuilder.getInstance(this.templateRenderer, this.jqueryWrapper, this.locStrings, this.ajax, this.facebook, this.viewManager);
};

DiscardAreaBuilderTest.prototype.trigger = function() {
	return this.testObj.buildDiscardArea(this.status, this.cardElements, this.gameId, this.currentPlayerId);
};

DiscardAreaBuilderTest.prototype.trainAreaTemplate = function(expectedLeaderHtml) {
	when(this.templateRenderer).renderTemplate("discard", allOf(
		hasMember("discardMessage", this.locStrings.discardMessage)
	)).thenReturn(this.discardHtml);
};
