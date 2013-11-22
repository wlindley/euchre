PreviousTrickDisplayBuilderTest = TestCase("PreviousTrickDisplayBuilderTest");

PreviousTrickDisplayBuilderTest.prototype.setUp = function() {
	this.playerId = "12345";

	this.players = [this.playerId, "2", "3", "4"];
	this.winnerId = this.playerId;
	this.cards = [{"suit" : 0, "value" : 9}, {"suit" : 3, "value" : 12}, {"suit" : 1, "value" : 13}, {"suit" : 2, "value" : 10}]; //make sure all suits and values are different
	this.cardHtmls = ["card 1", "card 2", "card 3", "card 4"];
	this.trickElementHtmls = ["trick element 1", "trick element 2", "trick element 3", "trick element 4"];
	this.cardElements = [];
	this.trickElementElements = [];
	this.previousTrick = {};
	this.cardSelector = mock(TEST.FakeJQueryElement);
	this.playerNamePromises = [];
	this.playerNameElements = [];
	for (var i in this.players) {
		this.previousTrick[this.players[i]] = this.cards[i];
		this.cardElements[i] = mock(TEST.FakeJQueryElement);
		this.trickElementElements[i] = mock(TEST.FakeJQueryElement);
		this.playerNamePromises[i] = mock(AVOCADO.PlayerNamePromise);
		this.playerNameElements[i] = mock(TEST.FakeJQueryElement);
	}
	this.previousTrickHtml = "some previous trick html";
	this.winningCardHtml = "winning card html";
	this.playersCardHtml = "players card html";

	this.previousTrickElement = mock(TEST.FakeJQueryElement);
	this.previousTrickElementParent = mock(TEST.FakeJQueryElement);
	this.errorElement = mock(TEST.FakeJQueryElement);

	this.buttonElement = mock(TEST.FakeJQueryElement);

	this.templateRenderer = mock(AVOCADO.TemplateRenderer);
	this.jqueryWrapper = mock(AVOCADO.JQueryWrapper);
	this.playerNameDirectory = mock(AVOCADO.PlayerNameDirectory);

	this.buildTestObj();
	this.doTraining();
};

PreviousTrickDisplayBuilderTest.prototype.testReturnsExpectedJQueryObject = function() {
	var actualResult = this.trigger();
	assertEquals(this.previousTrickElement, actualResult);
};

PreviousTrickDisplayBuilderTest.prototype.testSetsClassOnWinningCardAndAppendsElement = function() {
	this.trigger();
	var winnerIndex = this.players.indexOf(this.winnerId);
	verify(this.trickElementElements[winnerIndex]).addClass("winningCard");
	verify(this.trickElementElements[winnerIndex]).append(this.winningCardHtml);
};

PreviousTrickDisplayBuilderTest.prototype.testHooksUpPlayerNamesToPromises = function() {
	this.trigger();
	for (var i in this.players) {
		verify(this.playerNamePromises[i]).registerForUpdates(this.playerNameElements[i]);
	}
};

PreviousTrickDisplayBuilderTest.prototype.testAddsClickHandlerToContinueButton = function() {
	var continueClickHandler = function() {};
	this.testObj.buildContinueClickHandler = mockFunction();
	when(this.testObj.buildContinueClickHandler)(this.previousTrickElement).thenReturn(continueClickHandler);

	this.trigger();

	verify(this.buttonElement).click(continueClickHandler);
};

PreviousTrickDisplayBuilderTest.prototype.testContinueClickHandlerHidesElementAndCallsCompleteHandler = function() {
	var event = {};
	var hideCompleteHandler = function() {};
	this.testObj.buildHideCompleteHandler = mockFunction();
	when(this.testObj.buildHideCompleteHandler)(this.previousTrickElement).thenReturn(hideCompleteHandler);

	this.testObj.buildContinueClickHandler(this.previousTrickElement)(event);

	verify(this.previousTrickElementParent).fadeOut(100, hideCompleteHandler);
};

PreviousTrickDisplayBuilderTest.prototype.testHideCompleteHandlerRemovesElement = function() {
	var event = {};
	this.testObj.buildHideCompleteHandler(this.previousTrickElement)(event);
	verify(this.previousTrickElementParent).remove();
};

PreviousTrickDisplayBuilderTest.prototype.testEmptyPlayedCardsFailsGracefully = function() {
	this.previousTrick = {};

	var result = this.trigger();

	assertEquals(this.errorElement, result);
};

PreviousTrickDisplayBuilderTest.prototype.testUndefinedPlayedCardsFailsGracefully = function() {
	this.previousTrick = undefined;

	var result = this.trigger();

	assertEquals(this.errorElement, result);
};

PreviousTrickDisplayBuilderTest.prototype.trigger = function() {
	return this.testObj.buildPreviousTrickDisplay(this.previousTrick, this.winnerId);
};

PreviousTrickDisplayBuilderTest.prototype.doTraining = function() {
	when(this.previousTrickElement).find("div.trickElement").thenReturn(this.cardSelector);
	when(this.previousTrickElement).parent().thenReturn(this.previousTrickElementParent);

	for (var i in this.players) {
		when(this.playerNameDirectory).getNamePromise(this.players[i]).thenReturn(this.playerNamePromises[i]);
		when(this.playerNamePromises[i]).getName().thenReturn("");

		when(this.trickElementElements[i]).find(".playerName").thenReturn(this.playerNameElements[i]);
	}

	for (var i in this.cards) {
		when(this.templateRenderer).renderTemplate("card", this.cards[i]).thenReturn(this.cardHtmls[i]);

		var suitSelector = mock(TEST.FakeJQueryElement);

		when(this.cardSelector).has("input.cardSuit[value=" + this.cards[i].suit + "]").thenReturn(suitSelector);
		when(suitSelector).has("input.cardValue[value=" + this.cards[i].value + "]").thenReturn(this.trickElementElements[i]);

		when(this.templateRenderer).renderTemplate("trickElement", hasMember("card", this.cardHtmls[i])).thenReturn(this.trickElementHtmls[i]);
	}

	when(this.previousTrickElement).find("button.continue").thenReturn(this.buttonElement);

	when(this.templateRenderer).renderTemplate("previousTrick", allOf(
		hasMember("card0", this.trickElementHtmls[0]),
		hasMember("card1", this.trickElementHtmls[1]),
		hasMember("card2", this.trickElementHtmls[2]),
		hasMember("card3", this.trickElementHtmls[3])
	)).thenReturn(this.previousTrickHtml);

	when(this.templateRenderer).renderTemplate("playersCard").thenReturn(this.playersCardHtml);
	when(this.templateRenderer).renderTemplate("winningCard").thenReturn(this.winningCardHtml);

	when(this.jqueryWrapper).getElement(this.previousTrickHtml).thenReturn(this.previousTrickElement);
	when(this.jqueryWrapper).getElement("<div />").thenReturn(this.errorElement);
};

PreviousTrickDisplayBuilderTest.prototype.buildTestObj = function() {
	this.testObj = AVOCADO.PreviousTrickDisplayBuilder.getInstance(this.templateRenderer, this.jqueryWrapper, this.playerNameDirectory);
};