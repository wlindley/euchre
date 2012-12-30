RoundPlayingAreaBuilderTest = TestCase("RoundPlayingAreaBuilderTest");

RoundPlayingAreaBuilderTest.prototype.setUp = function() {
	this.templateRenderer = mock(AVOCADO.TemplateRenderer);
	this.jqueryWrapper = mock(AVOCADO.JQueryWrapper);
	this.locStrings = {"suit_1" : "clubs", "suit_2" : "diamonds", "suit_3" : "spades", "suit_4" : "hearts", "player" : "Player %playerId%", "noCardsPlayed" : "blah blah blah"};

	this.status = "round_in_progress";
	this.ledSuit = Math.floor(Math.random() * 4) + 1;
	this.expectedLedSuitString = this.locStrings["suit_" + this.ledSuit];
	this.players = ["1234", "5678", "9012", "3456"];
	this.cards = [{"suit" : 4, "value" : 11}, {"suit" : 4, "value" : 13}, {"suit" : 4, "value" : 9}, {"suit" : 4, "value" : 12}];
	this.cardHtmls = ["card html 1", "card html 2", "card html 3", "card html 4"];
	this.trickElementHtml = ["trick element 1", "trick element 2", "trick element 3", "trick element 4"];
	this.trainCardAndTrickElementTemplates();

	this.playingRoundHtml = "some HTML for playing the round";
	this.trainAreaTemplate();

	this.playingRoundElement = mock(TEST.FakeJQueryElement);
	when(this.jqueryWrapper).getElement(this.playingRoundHtml).thenReturn(this.playingRoundElement);

	this.buildTestObj();
};

RoundPlayingAreaBuilderTest.prototype.testReturnsExpectedJQueryElement = function() {
	var actualResult = this.trigger();
	assertEquals(this.playingRoundElement, actualResult);
};

RoundPlayingAreaBuilderTest.prototype.testReturnsNullWhenStatusIsNotRoundInProgress = function() {
	this.status = "trump_selection";
	
	var actualResult = this.trigger();
	assertEquals(null, actualResult);
};

RoundPlayingAreaBuilderTest.prototype.testUsesNoCardsPlayedLocStringWhenLedSuitIsZero = function() {
	this.ledSuit = 0;
	this.expectedLedSuitString = this.locStrings["noCardsPlayed"];
	this.templateRenderer = mock(AVOCADO.TemplateRenderer);
	this.trainCardAndTrickElementTemplates();
	this.trainAreaTemplate();
	this.buildTestObj();

	var actualResult = this.trigger();
	assertEquals(this.playingRoundElement, actualResult);
};

RoundPlayingAreaBuilderTest.prototype.buildTestObj = function() {
	this.testObj = AVOCADO.RoundPlayingAreaBuilder.getInstance(this.templateRenderer, this.jqueryWrapper, this.locStrings);
};

RoundPlayingAreaBuilderTest.prototype.trigger = function() {
	return this.testObj.buildRoundPlayingArea(this.status, this.ledSuit, this.trick);
};

RoundPlayingAreaBuilderTest.prototype.trainCardAndTrickElementTemplates = function() {
	this.trick = {};
	this.trickHtml = "";
	for (var i = 0; i < this.players.length; i++) {
		when(this.templateRenderer).renderTemplate("card", allOf(
			hasMember("suit", this.cards[i].suit),
			hasMember("value", this.cards[i].value)
		)).thenReturn(this.cardHtmls[i]);
		this.trick[this.players[i]] = this.cards[i];
		when(this.templateRenderer).renderTemplate("trickElement", allOf(
			hasMember("player", "Player " + this.players[i]),
			hasMember("card", this.cardHtmls[i])
		)).thenReturn(this.trickElementHtml[i]);
		this.trickHtml += this.trickElementHtml[i];
	}
};

RoundPlayingAreaBuilderTest.prototype.trainAreaTemplate = function() {
	when(this.templateRenderer).renderTemplate("playingRound", allOf(
		hasMember("ledSuit", this.expectedLedSuitString),
		hasMember("currentTrick", this.trickHtml)
	)).thenReturn(this.playingRoundHtml);
};
