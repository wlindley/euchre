GamePlayViewTest = TestCase("GamePlayViewTest");

GamePlayViewTest.prototype.setUp = function() {
	this.locStrings = {"trumpDisplay" : "trump - %trumpSuit%", "suit_1" : "h", "suit_2" : "s", "suit_3" : "d", "suit_4" : "c", "n/a" : "na na na nananana", "awesome status" : "the best status"};
	this.gameId = "34827";
	this.playerId = "12345";
	this.currentPlayerId = this.playerId;
	this.playerIds = [this.playerId, "2", "3", "4"];
	this.playerNamePromises = [];
	for (var i = 0; i < this.playerIds.length; i++) {
		this.playerNamePromises.push(mock(AVOCADO.PlayerNamePromise));
	}
	this.teams = [[this.playerId, "2"], ["3", "4"]];
	this.gameScores = [Math.floor(Math.random() * 11), Math.floor(Math.random() * 11)];
	this.roundScores = [Math.floor(Math.random() * 5), Math.floor(Math.random() * 5)];
	this.trumpSuit = Math.floor(Math.random() * 4) + 1;
	this.dealerId = "098765";
	this.blackListedSuits = [3];
	this.hand = [{"suit" : 2, "value" : 8}, {"suit" : 3, "value" : 10}, {"suit" : 1, "value" : 12}];
	this.upCard = {"suit" : 4, "value" : 12};
	this.status = "awesome status";
	this.ledSuit = Math.floor(Math.random() * 4) + 1;
	this.trick = "a bunch of trick data";
	this.previousTrick = "a previous trick's data";
	this.winnerId = "54321";
	this.cardHtmls = [];
	this.cardsElement = mock(TEST.FakeJQueryElement);
	this.completeCardHtml = "";
	for (var i = 0; i < this.hand.length; i++) {
		var curHtml = "card " + i;
		this.cardHtmls.push(curHtml);
		this.completeCardHtml += curHtml;
	}
	this.handHtml = "the whole hand";
	this.handElement = mock(TEST.FakeJQueryElement);
	this.viewGameListElement = mock(TEST.FakeJQueryElement);
	this.trumpSelectionElement = mock(TEST.FakeJQueryElement);
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
	this.previousTrickElement = mock(TEST.FakeJQueryElement);
	this.previousTrickInsertionElement = mock(TEST.FakeJQueryElement);
	this.turnElement = mock(TEST.FakeJQueryElement);
	this.turnNameElement = mock(TEST.FakeJQueryElement);
	this.gameCompleteElement = mock(TEST.FakeJQueryElement);
	this.gameCompleteInsertionElement = mock(TEST.FakeJQueryElement);

	this.ajax = mock(AVOCADO.Ajax);
	this.facebook = mock(AVOCADO.Facebook);
	this.templateRenderer = mock(AVOCADO.TemplateRenderer);
	this.gamePlayDiv = mock(TEST.FakeJQueryElement);
	this.viewManager = mock(AVOCADO.ViewManager);
	this.trumpSelectionAreaBuilder = mock(AVOCADO.TrumpSelectionAreaBuilder);
	this.roundPlayingAreaBuilder = mock(AVOCADO.RoundPlayingAreaBuilder);
	this.discardAreaBuilder = mock(AVOCADO.DiscardAreaBuilder);
	this.previousTrickDisplayBuilder = mock(AVOCADO.PreviousTrickDisplayBuilder);
	this.jqueryWrapper = mock(AVOCADO.JQueryWrapper);
	this.playerNameDirectory = mock(AVOCADO.PlayerNameDirectory);
	this.gameCompleteDisplayBuilder = mock(AVOCADO.GameCompleteDisplayBuilder);
	this.teamUtils = AVOCADO.TeamUtils.getInstance(this.facebook);

	this.ajaxPromise = mock(TEST.FakePromise);
	when(this.ajax).call(anything(), anything()).thenReturn(this.ajaxPromise);

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
			"blackListedSuits" : this.blackListedSuits,
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
		},
		"previousTrick" : {
			"playedCards" : this.previousTrick,
			"winnerId" : this.winnerId
		}
	};
}

GamePlayViewTest.prototype.doTraining = function() {
	when(this.facebook).getSignedInPlayerId().thenReturn(this.playerId);

	for (var i = 0; i < this.playerIds.length; i++) {
		when(this.playerNameDirectory).getNamePromise(this.playerIds[i]).thenReturn(this.playerNamePromises[i]);
	}

	when(this.gameElement).find(".hand").thenReturn(this.handElement);
	when(this.handElement).find(".card").thenReturn(this.cardsElement);
	for (var i = 0; i < this.hand.length; i++) {
		when(this.templateRenderer).renderTemplate("card", allOf(hasMember("suit", this.hand[i].suit), hasMember("value", this.hand[i].value))).thenReturn(this.cardHtmls[i]);
	}
	when(this.templateRenderer).renderTemplate("hand", hasMember("hand", this.completeCardHtml)).thenReturn(this.handHtml);
	when(this.gamePlayDiv).find(".viewGameList").thenReturn(this.viewGameListElement);
	when(this.trumpSelectionAreaBuilder).buildTrumpSelectionArea(allOf(hasMember("suit", this.upCard.suit), hasMember("value", this.upCard.value)), this.status, this.gameId, this.dealerId, this.currentPlayerId, this.teams, this.blackListedSuits).thenReturn(this.trumpSelectionElement);
	var trumpString = this.locStrings["suit_" + this.trumpSuit];
	if (!(("suit_" + this.trumpSuit) in this.locStrings)) {
		trumpString = this.locStrings["n/a"];
	}
	when(this.templateRenderer).renderTemplate("game", allOf(hasMember("hand", this.handHtml), hasMember("gameScores", this.gameScoresHtml), hasMember("roundScores", this.roundScoresHtml), hasMember("trump", trumpString), hasMember("status", this.locStrings[this.status]))).thenReturn(this.gameHtml);
	when(this.jqueryWrapper).getElement(this.gameHtml).thenReturn(this.gameElement);
	when(this.gameElement).find(".trumpSelection").thenReturn(this.trumpSelectionInsertionElement);
	when(this.gameElement).find(".playingRound").thenReturn(this.roundPlayingInsertionElement);
	when(this.gameElement).find(".discard").thenReturn(this.discardInsertionElement);
	when(this.gameElement).find(".previousTrickWrapper").thenReturn(this.previousTrickInsertionElement);
	when(this.gameElement).find(".gameCompleteWrapper").thenReturn(this.gameCompleteInsertionElement);
	when(this.gameElement).find(".card").thenReturn(this.cardElements);
	when(this.roundPlayingAreaBuilder).buildRoundPlayingArea(this.status, this.ledSuit, this.trick, this.cardElements, this.gameId, this.currentPlayerId, this.leaderId, this.teams).thenReturn(this.roundPlayingElement);
	when(this.discardAreaBuilder).buildDiscardArea(this.status, this.cardElements, this.gameId, this.currentPlayerId).thenReturn(this.discardElement);
	when(this.previousTrickDisplayBuilder).buildPreviousTrickDisplay(this.previousTrick, this.winnerId, this.teams).thenReturn(this.previousTrickElement);
	when(this.gameCompleteDisplayBuilder).buildGameCompleteDisplay(this.teams, this.gameScores, this.gameId).thenReturn(this.gameCompleteElement);

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
	when(this.gameElement).find(".turn").thenReturn(this.turnElement);
	when(this.turnElement).find(".playerName").thenReturn(this.turnNameElement);
};

GamePlayViewTest.prototype.trigger = function() {
	this.testObj.show({"gameId" : this.gameId});
	this.ajax.resolveCall(this.response);
};

GamePlayViewTest.prototype.setupFakeAjax = function() {
	this.templateRenderer = mock(AVOCADO.TemplateRenderer);
	this.ajax = new TEST.FakeAjax();

	this.buildResponseObj();
	this.doTraining();
	this.buildTestObj();
};

GamePlayViewTest.prototype.verifyCorrectView = function(status) {
	verify(this.gamePlayDiv).empty();
	if ("complete" == status) {
		verify(this.gameCompleteInsertionElement).append(this.gameCompleteElement);
		verify(this.trumpSelectionInsertionElement, never()).append(this.trumpSelectionElement);
		verify(this.roundPlayingInsertionElement, never()).append(this.roundPlayingElement);
		verify(this.discardInsertionElement, never()).append(this.discardElement);
	} else {
		verify(this.gameCompleteInsertionElement, never()).append(this.gameCompleteElement);
		verify(this.trumpSelectionInsertionElement).append(this.trumpSelectionElement);
		verify(this.roundPlayingInsertionElement).append(this.roundPlayingElement);
		verify(this.discardInsertionElement).append(this.discardElement);
	}
	verify(this.gamePlayDiv).append(this.gameElement);
	verify(this.viewGameListElement).click(this.testObj.handleViewGameListClick);
	verify(this.previousTrickInsertionElement).append(this.previousTrickElement);
	verify(this.gamePlayDiv).show();

	if (null !== this.currentPlayerId) {
		if ((this.teams[0].indexOf(this.currentPlayerId) == -1) != ((this.teams[0].indexOf(this.playerId) == -1))) {
			verify(this.turnNameElement).addClass("red");
		} else {
			verify(this.turnNameElement).addClass("green");
		}
	}
};

GamePlayViewTest.prototype.testInitRegistersWithViewManager = function() {
	this.testObj.init();
	verify(this.viewManager).registerView("gamePlay", this.testObj);
};

GamePlayViewTest.prototype.testShowCallsAjaxCorrectly = function() {
	this.testObj.show({"gameId" : this.gameId});
	verify(this.ajax).call("getGameData", allOf(hasMember("playerId", equalTo(this.playerId)), hasMember("gameId", equalTo(this.gameId))));
};

GamePlayViewTest.prototype.testShowRendersResponseCorrectly = function() {
	this.ajax = new TEST.FakeAjax();
	this.buildTestObj();

	this.trigger();

	this.verifyCorrectView(this.status);
};

GamePlayViewTest.prototype.testHandlesOtherTurn = function() {
	var otherPlayerId = this.playerIds[2];
	this.currentPlayerId = otherPlayerId;
	this.setupFakeAjax();

	this.trigger();

	this.verifyCorrectView(this.status);
};

GamePlayViewTest.prototype.testHandlesNullTurn = function() {
	this.currentPlayerId = null;
	this.setupFakeAjax();

	this.trigger();

	this.verifyCorrectView(this.status);
	verify(this.turnNameElement).text(this.locStrings["n/a"]);
};

GamePlayViewTest.prototype.testHandlesCompletedGame = function() {
	this.trumpSuit = 100;
	this.status = "complete";
	this.currentPlayerId = null;
	this.setupFakeAjax();

	this.trigger();

	this.verifyCorrectView(this.status);
	verify(this.handElement).hide();
};

GamePlayViewTest.prototype.testHooksUpNamePromiseForTurn = function() {
	for (var i = 0; i < this.playerIds.length; i++) {
		this.currentPlayerId = this.playerIds[i];
		this.setupFakeAjax();

		this.trigger();

		verify(this.playerNamePromises[i]).registerForUpdates(this.turnNameElement);
	}
}

GamePlayViewTest.prototype.testSwapsScoresWhenPlayerIsOnSecondTeam = function() {
	this.teams = [this.teams[1], this.teams[0]];
	this.setupFakeAjax();

	this.trigger();

	this.verifyCorrectView(this.status);
};

GamePlayViewTest.prototype.testShowsNoTrumpSuitWhenNoTrumpSelected = function() {
	this.trumpSuit = 0;
	this.setupFakeAjax();

	this.trigger();

	this.verifyCorrectView(this.status);
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
	this.testObj = new AVOCADO.GamePlayView(this.ajax, this.facebook, this.templateRenderer, this.gamePlayDiv, this.viewManager, this.locStrings, this.trumpSelectionAreaBuilder, this.jqueryWrapper, this.roundPlayingAreaBuilder, this.discardAreaBuilder, this.previousTrickDisplayBuilder, this.playerNameDirectory, this.gameCompleteDisplayBuilder, this.teamUtils);
};
