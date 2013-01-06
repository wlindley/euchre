GamePlayViewTest = TestCase("GamePlayViewTest");

GamePlayViewTest.prototype.setUp = function() {
	this.locStrings = {"yourTurn" : "Your turn", "otherTurn" : "Other turn %playerId%", "trumpDisplay" : "trump - %trumpSuit%", "suit_1" : "h", "suit_2" : "s", "suit_3" : "d", "suit_4" : "c"};
	this.gameId = "34827";
	this.playerId = "12345";
	this.currentPlayerId = this.playerId;
	this.playerIds = [this.playerId, "2", "3", "4"];
	this.teams = [[this.playerId, "2"], ["3", "4"]];
	this.gameScores = [Math.floor(Math.random() * 11), Math.floor(Math.random() * 11)];
	this.roundScores = [Math.floor(Math.random() * 5), Math.floor(Math.random() * 5)];
	this.trumpSuit = Math.floor(Math.random() * 4) + 1;
	this.dealerId = "098765";
	this.hand = [{"suit" : 2, "value" : 8}, {"suit" : 3, "value" : 10}, {"suit" : 1, "value" : 12}];
	this.upCard = {"suit" : 4, "value" : 12};
	this.status = "awesome status";
	this.ledSuit = Math.floor(Math.random() * 4) + 1;
	this.trick = "a bunch of trick data";
	this.cardHtmls = [];
	this.completeCardHtml = "";
	for (var i = 0; i < this.hand.length; i++) {
		var curHtml = "card " + i;
		this.cardHtmls.push(curHtml);
		this.completeCardHtml += curHtml;
	}
	this.handHtml = "the whole hand";
	this.viewGameListElement = mock(TEST.FakeJQueryElement);
	this.trumpSelectionElement = mock(TEST.FakeJQueryElement);
	this.expectedTurn = this.locStrings.yourTurn;
	this.gameHtml = "the whole game";
	this.gameElement = mock(TEST.FakeJQueryElement);
	this.trumpSelectionInsertionElement = mock(TEST.FakeJQueryElement);
	this.roundPlayingInsertionElement = mock(TEST.FakeJQueryElement);
	this.cardElements = mock(TEST.FakeJQueryElement);
	this.roundPlayingElement = mock(TEST.FakeJQueryElement);
	this.gameScoresHtml = "game scores for both teams";
	this.roundScoresHtml = "round scores for both teams";
	this.leaderId = this.playerIds[Math.floor(Math.random() * this.playerIds.length)];
	this.discardInsertionElement = mock(TEST.FakeJQueryElement);
	this.discardElement = mock(TEST.FakeJQueryElement);

	this.ajax = mock(AVOCADO.Ajax);
	this.templateRenderer = mock(AVOCADO.TemplateRenderer);
	this.gamePlayDiv = mock(TEST.FakeJQueryElement);
	this.viewManager = mock(AVOCADO.ViewManager);
	this.trumpSelectionAreaBuilder = mock(AVOCADO.TrumpSelectionAreaBuilder);
	this.roundPlayingAreaBuilder = mock(AVOCADO.RoundPlayingAreaBuilder);
	this.discardAreaBuilder = mock(AVOCADO.DiscardAreaBuilder);
	this.jqueryWrapper = mock(AVOCADO.JQueryWrapper);

	this.buildResponseObj();
	this.doTraining();
	this.buildTestObj();
};

GamePlayViewTest.prototype.buildResponseObj = function() {
	this.response = {
		"success" : true,
		"gameId" : this.gameId,
		"status" : this.status,
		"playerIds" : this.playerIds,
		"teams" : this.teams,
		"scores" : this.gameScores,
		"round" : {
			"hand" : this.hand,
			"currentPlayerId" : this.currentPlayerId,
			"upCard" : this.upCard, "dealerId" : this.dealerId,
			"trump" : this.trumpSuit,
			"dealerId" : this.dealerId,
			"tricksTaken" : this.roundScores,
			"currentTrick" : {
				"ledSuit" : this.ledSuit,
				"playedCards" : this.trick,
				"leaderId" : this.leaderId
			}
		}
	};
}

GamePlayViewTest.prototype.doTraining = function() {
	this.expectedTrumpText = "";
	if (0 < this.trumpSuit) {
		this.expectedTrumpText = this.locStrings.trumpDisplay.replace("%trumpSuit%", this.locStrings["suit_" + this.trumpSuit]);
	}

	for (var i = 0; i < this.hand.length; i++) {
		when(this.templateRenderer).renderTemplate("card", allOf(hasMember("suit", this.hand[i].suit), hasMember("value", this.hand[i].value))).thenReturn(this.cardHtmls[i]);
	}
	when(this.templateRenderer).renderTemplate("hand", hasMember("hand", this.completeCardHtml)).thenReturn(this.handHtml);
	when(this.gamePlayDiv).find(".viewGameList").thenReturn(this.viewGameListElement);
	when(this.trumpSelectionAreaBuilder).buildTrumpSelectionArea(allOf(hasMember("suit", this.upCard.suit), hasMember("value", this.upCard.value)), equalTo(this.status), equalTo(this.gameId), equalTo(this.dealerId), equalTo(this.currentPlayerId)).thenReturn(this.trumpSelectionElement);
	when(this.templateRenderer).renderTemplate("game", allOf(hasMember("gameId", this.gameId), hasMember("hand", this.handHtml), hasMember("turn", this.expectedTurn), hasMember("gameScores", this.gameScoresHtml), hasMember("roundScores", this.roundScoresHtml), hasMember("trump", this.expectedTrumpText))).thenReturn(this.gameHtml);
	when(this.jqueryWrapper).getElement(this.gameHtml).thenReturn(this.gameElement);
	when(this.gameElement).find(".trumpSelection").thenReturn(this.trumpSelectionInsertionElement);
	when(this.gameElement).find(".playingRound").thenReturn(this.roundPlayingInsertionElement);
	when(this.gameElement).find(".discard").thenReturn(this.discardInsertionElement);
	when(this.gameElement).find(".card").thenReturn(this.cardElements);
	when(this.roundPlayingAreaBuilder).buildRoundPlayingArea(this.status, this.ledSuit, this.trick, this.cardElements, this.gameId, this.currentPlayerId, this.leaderId, this.teams).thenReturn(this.roundPlayingElement);
	when(this.discardAreaBuilder).buildDiscardArea(this.status, this.cardElements, this.gameId, this.currentPlayerId).thenReturn(this.discardElement);

	var yourTeamScore = this.gameScores[0];
	var otherTeamScore = this.gameScores[1];
	var yourTeamRoundScore = this.roundScores[0];
	var otherTeamRoundScore = this.roundScores[1];
	if (0 <= this.teams[1].indexOf(this.playerId)) {
		yourTeamScore = this.gameScores[1];
		otherTeamScore = this.gameScores[0];
		yourTeamRoundScore = this.roundScores[1];
		otherTeamRoundScore = this.roundScores[0];
	}
	when(this.templateRenderer).renderTemplate("gameScores", allOf(hasMember("yourScore", yourTeamScore), hasMember("otherScore", otherTeamScore))).thenReturn(this.gameScoresHtml);
	when(this.templateRenderer).renderTemplate("roundScores", allOf(hasMember("yourScore", yourTeamRoundScore), hasMember("otherScore", otherTeamRoundScore))).thenReturn(this.roundScoresHtml);
};

GamePlayViewTest.prototype.verifyCorrectView = function() {
	verify(this.gamePlayDiv).empty();
	verify(this.trumpSelectionInsertionElement).append(this.trumpSelectionElement);
	verify(this.roundPlayingInsertionElement).append(this.roundPlayingElement);
	verify(this.discardInsertionElement).append(this.discardElement);
	verify(this.gamePlayDiv).append(this.gameElement);
	verify(this.viewGameListElement).click(this.testObj.handleViewGameListClick);
	verify(this.gamePlayDiv).show();
};

GamePlayViewTest.prototype.testInitRegistersWithViewManager = function() {
	this.testObj.init();
	verify(this.viewManager).registerView("gamePlay", this.testObj);
};

GamePlayViewTest.prototype.testShowCallsAjaxCorrectly = function() {
	this.testObj.show({"gameId" : this.gameId});
	verify(this.ajax).call("getGameData", allOf(hasMember("playerId", equalTo(this.playerId)), hasMember("gameId", equalTo(this.gameId))), func());
};

GamePlayViewTest.prototype.testShowRendersResponseCorrectly = function() {
	this.ajax = new TEST.FakeAjax();
	this.buildTestObj();

	this.ajax.callbackResponse = this.response;

	this.testObj.show({"gameId" : this.gameId});

	this.verifyCorrectView();
};

GamePlayViewTest.prototype.testHandlesOtherTurn = function() {
	var otherPlayerId = "4320987";
	this.currentPlayerId = otherPlayerId;
	this.expectedTurn = this.locStrings.otherTurn.replace("%playerId%", otherPlayerId);

	this.templateRenderer = mock(AVOCADO.TemplateRenderer);
	this.ajax = new TEST.FakeAjax();

	this.buildResponseObj();
	this.doTraining();
	this.buildTestObj();

	this.ajax.callbackResponse = this.response;

	this.testObj.show({"gameId" : this.gameId});

	this.verifyCorrectView();
};

GamePlayViewTest.prototype.testSwapsScoresWhenPlayerIsOnSecondTeam = function() {
	this.teams = [this.teams[1], this.teams[0]];

	this.templateRenderer = mock(AVOCADO.TemplateRenderer);
	this.ajax = new TEST.FakeAjax();

	this.buildResponseObj();
	this.doTraining();
	this.buildTestObj();

	this.ajax.callbackResponse = this.response;

	this.testObj.show({"gameId" : this.gameId});

	this.verifyCorrectView();
};

GamePlayViewTest.prototype.testShowsNoTrumpSuitWhenNoTrumpSelected = function() {
	this.trumpSuit = 0;

	this.templateRenderer = mock(AVOCADO.TemplateRenderer);
	this.ajax = new TEST.FakeAjax();

	this.buildResponseObj();
	this.doTraining();
	this.buildTestObj();

	this.ajax.callbackResponse = this.response;

	this.testObj.show({"gameId" : this.gameId});

	this.verifyCorrectView();
};

GamePlayViewTest.prototype.testHideHidesDiv = function() {
	this.testObj.hide();
	verify(this.gamePlayDiv).hide();
};

GamePlayViewTest.prototype.testClickHandlerCallsViewManager = function() {
	this.testObj.handleViewGameListClick();
	verify(this.viewManager).showView("gameList");
};

GamePlayViewTest.prototype.buildTestObj = function() {
	this.testObj = new AVOCADO.GamePlayView(this.ajax, this.playerId, this.templateRenderer, this.gamePlayDiv, this.viewManager, this.locStrings, this.trumpSelectionAreaBuilder, this.jqueryWrapper, this.roundPlayingAreaBuilder, this.discardAreaBuilder);
};
