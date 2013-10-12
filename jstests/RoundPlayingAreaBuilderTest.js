RoundPlayingAreaBuilderTest = TestCase("RoundPlayingAreaBuilderTest");

RoundPlayingAreaBuilderTest.prototype.setUp = function() {
	this.playerId = "123456";
	this.currentPlayerId = "123456";
	this.gameId = 908234;
	this.templateRenderer = mock(AVOCADO.TemplateRenderer);
	this.jqueryWrapper = mock(AVOCADO.JQueryWrapper);
	this.locStrings = {"suit_1" : "clubs", "suit_2" : "diamonds", "suit_3" : "spades", "suit_4" : "hearts", "player" : "Player %playerId%", "noCardsPlayed" : "blah blah blah", "yourTeam" : "team 1", "otherTeam" : "team 2"};
	this.teams = [[this.playerId, "1234"], ["5678", "9012"]];
	this.leaderId = this.teams[Math.floor(Math.random() * 2)][Math.floor(Math.random() * 2)];
	this.leaderHtml = "some leader html";
	this.leaderName = this.locStrings.player.replace("%playerId%", this.leaderId);
	this.leaderTeamString = this.locStrings.yourTeam;
	if (this.teams[1].indexOf(this.leaderId) >= 0) {
		this.leaderTeamString = this.locStrings.otherTeam;
	}

	this.status = "round_in_progress";
	this.ledSuit = Math.floor(Math.random() * 4) + 1;
	this.expectedLedSuitString = this.locStrings["suit_" + this.ledSuit];
	this.players = ["1234", "5678", "9012", "3456"];
	this.cards = [{"suit" : 4, "value" : 11}, {"suit" : 4, "value" : 13}, {"suit" : 4, "value" : 9}, {"suit" : 4, "value" : 12}];
	this.cardHtmls = ["card html 1", "card html 2", "card html 3", "card html 4"];
	this.trickElementHtml = ["trick element 1", "trick element 2", "trick element 3", "trick element 4"];
	this.trainCardAndTrickElementTemplates();

	this.playingRoundHtml = "some HTML for playing the round";
	this.trainAreaTemplate(this.leaderHtml);

	this.playingRoundElement = mock(TEST.FakeJQueryElement);
	when(this.jqueryWrapper).getElement(this.playingRoundHtml).thenReturn(this.playingRoundElement);

	this.cardElements = mock(TEST.FakeJQueryElement);

	this.ajax = mock(AVOCADO.Ajax);

	this.viewManager = mock(AVOCADO.ViewManager);

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
	this.trainAreaTemplate(this.leaderHtml);
	this.buildTestObj();

	var actualResult = this.trigger();
	assertEquals(this.playingRoundElement, actualResult);
};

RoundPlayingAreaBuilderTest.prototype.testUsesEmptyStringForTrickLeaderWhenTrickLeaderIsNull = function() {
	this.leaderId = null;
	this.leaderHtml = "some leader html";
	this.templateRenderer = mock(AVOCADO.TemplateRenderer);
	this.trainCardAndTrickElementTemplates();
	this.trainAreaTemplate("");
	this.buildTestObj();

	var actualResult = this.trigger();
	assertEquals(this.playingRoundElement, actualResult);
};

RoundPlayingAreaBuilderTest.prototype.testAddsClickHandlersAndClassToCardImages = function() {
	var cardClickHandler = function() {};
	this.testObj.buildCardClickHandler = mockFunction();
	when(this.testObj.buildCardClickHandler)(this.gameId).thenReturn(cardClickHandler);

	this.trigger();

	verify(this.cardElements).addClass("clickableCard");
	verify(this.cardElements).click(cardClickHandler);
};

RoundPlayingAreaBuilderTest.prototype.testHandleCardClickCallsAjaxCorrectly = function() {
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

	verify(this.ajax).call("playCard", allOf(
		hasMember("playerId", this.playerId),
		hasMember("gameId", this.gameId),
		hasMember("suit", suit),
		hasMember("value", value)
	), refreshViewFunc);
};

RoundPlayingAreaBuilderTest.prototype.testRefreshViewFuncCallsViewManagerCorrectly = function() {
	var origFunc = setTimeout;

	var testHarness = this;

	var hasCalledAsync = false;
	setTimeout = function (func, time, lang) {
		hasCalledAsync = true;
		verify(testHarness.viewManager, never()).showView("gamePlay", allOf(hasMember("gameId", testHarness.gameId), hasMember("playerId", testHarness.playerId)));
		func();
		verify(testHarness.viewManager).showView("gamePlay", allOf(hasMember("gameId", testHarness.gameId), hasMember("playerId", testHarness.playerId)));
	};

	this.testObj.buildRefreshViewFunc(this.gameId)();
	assertTrue(hasCalledAsync);

	setTimeout = origFunc;
};

RoundPlayingAreaBuilderTest.prototype.testDoesNotBindClickHandlersIfNotCurrentPlayersTurn = function() {
	this.currentPlayerId = "7890123";
	this.trigger();
	verify(this.cardElements, never()).addClass("clickableCard");
	verify(this.cardElements, never()).click(func());
};

RoundPlayingAreaBuilderTest.prototype.buildTestObj = function() {
	this.testObj = AVOCADO.RoundPlayingAreaBuilder.getInstance(this.templateRenderer, this.jqueryWrapper, this.locStrings, this.ajax, this.playerId, this.viewManager);
};

RoundPlayingAreaBuilderTest.prototype.trigger = function() {
	return this.testObj.buildRoundPlayingArea(this.status, this.ledSuit, this.trick, this.cardElements, this.gameId, this.currentPlayerId, this.leaderId, this.teams);
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

RoundPlayingAreaBuilderTest.prototype.trainAreaTemplate = function(expectedLeaderHtml) {
	when(this.templateRenderer).renderTemplate("leader", allOf(
		hasMember("leaderName", this.leaderName),
		hasMember("team", this.leaderTeamString)
	)).thenReturn(this.leaderHtml);
	when(this.templateRenderer).renderTemplate("playingRound", allOf(
		hasMember("ledSuit", this.expectedLedSuitString),
		hasMember("currentTrick", this.trickHtml),
		hasMember("leader", expectedLeaderHtml)
	)).thenReturn(this.playingRoundHtml);
};
