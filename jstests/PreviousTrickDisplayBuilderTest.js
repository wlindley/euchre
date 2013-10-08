PreviousTrickDisplayBuilderTest = TestCase("PreviousTrickDisplayBuilderTest");

PreviousTrickDisplayBuilderTest.prototype.setUp = function() {
	this.locStrings = {};
	this.playerId = "12345";

	this.players = [this.playerId, "2", "3", "4"];
	this.winnerId = this.playerId;
	this.cards = [{"suit" : 0, "value" : 9}, {"suit" : 3, "value" : 12}, {"suit" : 1, "value" : 13}, {"suit" : 2, "value" : 10}]; //make sure all suits and values are different
	this.cardHtmls = ["card 1", "card 2", "card 3", "card 4"];
	this.cardElements = [];
	this.previousTrick = {};
	for (var i in this.players) {
		this.previousTrick[this.players[i]] = this.cards[i];
		this.cardElements[i] = mock(TEST.FakeJQueryElement);
	}
	this.previousTrickHtml = "some previous trick html";
	this.winningCardHtml = "winning card html";
	this.playersCardHtml = "players card html";

	this.previousTrickElement = mock(TEST.FakeJQueryElement);
	this.errorElement = mock(TEST.FakeJQueryElement);

	this.buttonElement = mock(TEST.FakeJQueryElement);

	this.templateRenderer = mock(AVOCADO.TemplateRenderer);
	this.jqueryWrapper = mock(AVOCADO.JQueryWrapper);

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
	verify(this.cardElements[winnerIndex]).addClass("winningCard");
	verify(this.cardElements[winnerIndex]).append(this.winningCardHtml);
};

PreviousTrickDisplayBuilderTest.prototype.testSetsClassOnPlayersCardAndAppendsElement = function() {
	this.trigger();
	var playerIndex = this.players.indexOf(this.playerId);
	verify(this.cardElements[playerIndex]).addClass("playersCard");
	verify(this.cardElements[playerIndex]).append(this.playersCardHtml);
};

PreviousTrickDisplayBuilderTest.prototype.testPlayersCardClassSetAddedBeforeWinningCardClass = function() {
	var playerIndex = this.players.indexOf(this.playerId);
	var winnerIndex = this.players.indexOf(this.winnerId);
	when(this.cardElements[playerIndex]).addClass("playersCard").thenThrow("First!");

	try
	{
		this.trigger();
	}
	catch (ex)
	{
		//intentionally empty
	}

	verify(this.cardElements[winnerIndex], never()).addClass("winningCard");
	verify(this.cardElements[winnerIndex], never()).append(this.winningCardHtml);
};

PreviousTrickDisplayBuilderTest.prototype.testAddsClickHandlerToContinueButton = function() {
	var continueClickHandler = function() {};
	this.testObj.buildContinueClickHandler = mockFunction();
	when(this.testObj.buildContinueClickHandler)(this.previousTrickElement).thenReturn(continueClickHandler);

	this.trigger();

	verify(this.buttonElement).click(continueClickHandler);
};

PreviousTrickDisplayBuilderTest.prototype.testContinueClickHandlerRemovesElement = function() {
	var event = {};

	this.testObj.buildContinueClickHandler(this.previousTrickElement)(event);

	verify(this.previousTrickElement).remove();
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
	var cardSelector = mock(TEST.FakeJQueryElement);
	when(this.previousTrickElement).find("div.card").thenReturn(cardSelector);

	for (var i in this.cards) {
		when(this.templateRenderer).renderTemplate("card", this.cards[i]).thenReturn(this.cardHtmls[i]);

		var suitSelector = mock(TEST.FakeJQueryElement);

		when(cardSelector).has("input.cardSuit[value=" + this.cards[i].suit + "]").thenReturn(suitSelector);
		when(suitSelector).has("input.cardValue[value=" + this.cards[i].value + "]").thenReturn(this.cardElements[i]);
	}

	when(this.previousTrickElement).find("button.continue").thenReturn(this.buttonElement);

	when(this.templateRenderer).renderTemplate("previousTrick", allOf(
		hasMember("card0", this.cardHtmls[0]),
		hasMember("card1", this.cardHtmls[1]),
		hasMember("card2", this.cardHtmls[2]),
		hasMember("card3", this.cardHtmls[3])
	)).thenReturn(this.previousTrickHtml);

	when(this.templateRenderer).renderTemplate("playersCard").thenReturn(this.playersCardHtml);
	when(this.templateRenderer).renderTemplate("winningCard").thenReturn(this.winningCardHtml);

	when(this.jqueryWrapper).getElement(this.previousTrickHtml).thenReturn(this.previousTrickElement);
	when(this.jqueryWrapper).getElement("<div />").thenReturn(this.errorElement);
};

PreviousTrickDisplayBuilderTest.prototype.buildTestObj = function() {
	this.testObj = AVOCADO.PreviousTrickDisplayBuilder.getInstance(this.templateRenderer, this.jqueryWrapper, this.locStrings, this.playerId);
};