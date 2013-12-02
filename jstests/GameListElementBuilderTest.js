GameListElementBuilderTest = TestCase("GameListElementBuilderTest");

GameListElementBuilderTest.prototype.setUp = function() {
	this.elementHtml = "html for list element";
	this.element = mock(TEST.FakeJQueryElement);
	this.gameId = "asdlkj324";
	this.playerId = "1209daslkj";
	this.otherPlayerId = "23klsadf39";
	this.team = [[this.otherPlayerId, "3456"], [this.playerId, "1234"]];
	this.currentPlayerId = this.playerId;
	this.requestTitle = "request title";
	this.requestMessage = "all of the request messages";

	this.element = mock(TEST.FakeJQueryElement);
	this.linkElement = mock(TEST.FakeJQueryElement);
	this.turnNameElement = mock(TEST.FakeJQueryElement);
	this.turnElement = mock(TEST.FakeJQueryElement);
	this.namePromises = {};
	this.tableElement = mock(TEST.FakeJQueryElement);
	this.tableDataElements = [];
	this.tableDataNameElements = [];
	this.team0Element = mock(TEST.FakeJQueryElement);
	this.team1Element = mock(TEST.FakeJQueryElement);

	this.jqueryWrapper = mock(AVOCADO.JQueryWrapper);
	this.templateRenderer = mock(AVOCADO.TemplateRenderer);
	this.locStrings = {
		"vs" : "some versus",
		"n/a" : "N/A",
		"inviteCTA" : "invite",
		"joinCTA" : "join",
		"round_in_progress" : "foo",
		"waiting_for_more_players" : "bar",
		"trump_selection" : "baz",
		"gameInviteTitle" : this.requestTitle,
		"gameInviteMessage" : this.requestMessage
	};
	this.playerNameDirectory = mock(AVOCADO.PlayerNameDirectory);
	this.facebook = mock(AVOCADO.Facebook);
	this.ajax = mock(AVOCADO.Ajax);
	this.viewManager = mock(AVOCADO.ViewManager);

	this.showGameDataFunc = mockFunction();
	this.gameInviteClickHandler = mockFunction();

	this.ajaxPromise = mock(TEST.FakePromise);
	when(this.ajax).call(anything(), anything()).thenReturn(this.ajaxPromise);

	this.origSetTimeout = setTimeout;
	setTimeout = function(func, time, lang) {
		func();
	};

	this.buildTestObj();
};

GameListElementBuilderTest.prototype.tearDown = function() {
	setTimeout = this.origSetTimeout;
};

GameListElementBuilderTest.prototype.buildTestObj = function() {
	this.testObj = new AVOCADO.GameListElementBuilder(this.jqueryWrapper, this.templateRenderer, this.locStrings, this.playerNameDirectory, this.facebook, this.ajax, this.viewManager);
};

GameListElementBuilderTest.prototype.doTraining = function(status) {
	this.status = status;
	this.gameData = {
		"gameId" : this.gameId,
		"status" : this.status,
		"currentPlayerId" : this.currentPlayerId,
		"teams" : this.team
	};

	when(this.templateRenderer).renderTemplate("gameListEntry", allOf(
		hasMember("vs", this.locStrings["vs"]),
		hasMember("gameId", this.gameId),
		hasMember("status", this.locStrings[status])
	)).thenReturn(this.elementHtml);
	when(this.jqueryWrapper).getElement(this.elementHtml).thenReturn(this.element);

	when(this.facebook).getSignedInPlayerId().thenReturn(this.playerId);

	this.namePromises[this.currentPlayerId] = mock(AVOCADO.PlayerNamePromise);
	for (var j = 0; j < 2; j++) {
		var teamTableElements = [];
		var teamNameElements = [];
		for (var k = 0; k < 2; k++) {
			if ((j in this.team) && (k in this.team[j])) {
				var pid = this.team[j][k];
				this.namePromises[pid] = mock(AVOCADO.PlayerNamePromise);
			}
			teamTableElements.push(mock(TEST.FakeJQueryElement));
			teamNameElements.push(mock(TEST.FakeJQueryElement));
		}
		this.tableDataElements.push(teamTableElements);
		this.tableDataNameElements.push(teamNameElements);
	}

	when(this.playerNameDirectory).getNamePromise(this.currentPlayerId).thenReturn(this.namePromises[this.currentPlayerId]);
	for (var pid in this.namePromises) {
		when(this.playerNameDirectory).getNamePromise(pid).thenReturn(this.namePromises[pid]);
	}

	when(this.element).find(".viewGameData").thenReturn(this.linkElement);
	when(this.element).find(".gameListElementTeams").thenReturn(this.tableElement);
	when(this.element).find(".turn").thenReturn(this.turnElement);
	when(this.element).find(".team0").thenReturn(this.team0Element);
	when(this.element).find(".team1").thenReturn(this.team1Element);
	when(this.turnElement).find(".playerName").thenReturn(this.turnNameElement);
	var tableDataSelector = mock(TEST.FakeJQueryElement);
	when(this.tableElement).find(".playerNameContainer").thenReturn(tableDataSelector);
	for (var j in this.tableDataElements) {
		var teamSelector = mock(TEST.FakeJQueryElement);
		when(tableDataSelector).has("input.team[value=" + j + "]").thenReturn(teamSelector);
		for (var k in this.tableDataElements[j]) {
			when(teamSelector).has("input.index[value=" + k + "]").thenReturn(this.tableDataElements[j][k]);
			when(this.tableDataElements[j][k]).find(".playerName").thenReturn(this.tableDataNameElements[j][k]);
		}
	}
};

GameListElementBuilderTest.prototype.trigger = function(isInvite) {
	return this.testObj.buildListElement(this.gameData, isInvite);
};

GameListElementBuilderTest.prototype.testBuildListElementReturnsExpectedObject = function() {
	this.doTraining("round_in_progress");
	assertEquals(this.element, this.trigger(true));
};

GameListElementBuilderTest.prototype.testHooksUpTurnNamePromise = function() {
	this.doTraining("trump_selection");
	this.trigger(true);
	verify(this.namePromises[this.currentPlayerId]).registerForUpdates(this.turnNameElement);
};

GameListElementBuilderTest.prototype.testSetsExpectedStringForNullCurrentPlayer = function() {
	this.currentPlayerId = null;
	this.doTraining("round_in_progress");
	this.trigger(true);
	verify(this.turnNameElement).text(this.locStrings["n/a"]);
};

GameListElementBuilderTest.prototype.testHooksUpTeamNamePromisesAndCTAs = function() {
	this.testObj.buildGameInviteClickHandler = mockFunction();
	when(this.testObj.buildGameInviteClickHandler)(this.gameId).thenReturn(this.gameInviteClickHandler);
	this.team = [this.team[0], [this.team[1][0]]];
	this.doTraining("waiting_for_more_players");
	this.trigger(true);
	for (var j = 0; j < 2; j++) {
		for (var k = 0; k < 2; k++) {
			if ((j in this.team) && (k in this.team[j])) {
				var pid = this.team[j][k];
				verify(this.namePromises[pid]).registerForUpdates(this.tableDataNameElements[j][k]);
			} else {
				verify(this.tableDataNameElements[j][k]).text(this.locStrings["inviteCTA"]);
				verify(this.tableDataElements[j][k]).addClass("clickable");
				verify(this.tableDataElements[j][k]).click(this.gameInviteClickHandler);
			}
		}
	}
};

GameListElementBuilderTest.prototype.testHooksUpTeamNamePromisesAndCTAsForJoining = function() {
	this.testObj.buildGameJoinClickHandler = mockFunction();
	var gameJoinClickHandlers = [[], []];
	for (var j = 0; j < 2; j++) {
		for (var k = 0; k < 2; k++) {
			gameJoinClickHandlers[j][k] = mockFunction();
			when(this.testObj.buildGameJoinClickHandler)(this.gameId, j).thenReturn(gameJoinClickHandlers[j][k]);
		}
	}
	this.team = [this.team[0], [this.team[1][1]]];
	this.doTraining("waiting_for_more_players");
	this.trigger(false);
	for (var j = 0; j < 2; j++) {
		for (var k = 0; k < 2; k++) {
			if ((j in this.team) && (k in this.team[j])) {
				var pid = this.team[j][k];
				verify(this.namePromises[pid]).registerForUpdates(this.tableDataNameElements[j][k]);
			} else {
				verify(this.tableDataNameElements[j][k]).text(this.locStrings["joinCTA"]);
				verify(this.tableDataElements[j][k]).addClass("clickable");
				verify(this.tableDataElements[j][k]).click(gameJoinClickHandlers[j][k]);
			}
		}
	}
};

GameListElementBuilderTest.prototype.testHooksUpClickHandler = function() {
	this.testObj.buildShowGameDataHandler = mockFunction();
	when(this.testObj.buildShowGameDataHandler)(this.gameId).thenReturn(this.showGameDataFunc);

	this.doTraining("round_in_progress");
	this.trigger(true);
	verify(this.linkElement).click(this.showGameDataFunc);
};

GameListElementBuilderTest.prototype.testDoesNotHookUpClickHandlerIfGameNotStarted = function() {
	this.currentPlayerId = null;
	this.doTraining("waiting_for_more_players");
	this.trigger(true);
	verify(this.linkElement, never()).click(this.showGameDataFunc);
};

GameListElementBuilderTest.prototype.testSetsCorrectClassesIfCurrentPlayersTurn = function() {
	this.doTraining("round_in_progress");
	this.trigger(true);
	verify(this.element).addClass("primary");
	verify(this.element).addClass("clickable");
};

GameListElementBuilderTest.prototype.testSetsCorrectClassesIfStatusIsWaitingForMorePlayers = function() {
	this.currentPlayerId = null;
	this.doTraining("waiting_for_more_players");
	this.trigger(true);
	verify(this.element).addClass("tertiary");
};

GameListElementBuilderTest.prototype.testSetsCorrectClassesIfNotLocalPlayersTurn = function() {
	this.currentPlayerId = this.otherPlayerId;
	this.doTraining("round_in_progress");
	this.trigger(true);
	verify(this.element).addClass("secondary");
	verify(this.element).addClass("clickable");
};

GameListElementBuilderTest.prototype.testAddsCorrectClassesForTeams = function() {
	this.doTraining("round_in_progress");
	this.trigger(true);
	verify(this.team0Element).addClass("red");
	verify(this.team1Element).addClass("green");
};

GameListElementBuilderTest.prototype.testAddsCorrectClassesForTeamsWhenLocalPlayerIsOnOtherTeam = function() {
	this.team = [this.team[1], this.team[0]];
	this.doTraining("round_in_progress");
	this.trigger(true);
	verify(this.team0Element).addClass("green");
	verify(this.team1Element).addClass("red");
};

GameListElementBuilderTest.prototype.testHandleGameInviteClickCallsFacebook = function() {
	this.team = [this.team[0], [this.team[1][0]]];
	this.doTraining("waiting_for_more_players");

	this.testObj.buildGameInviteClickHandler(this.gameId)();

	verify(this.facebook).sendRequests(this.requestTitle, this.requestMessage, hasMember("gameId", this.gameId));
};

GameListElementBuilderTest.prototype.testHandleGameJoinClickCallsAjax = function() {
	this.team = [this.team[0], [this.team[1][1]]];
	var expectedTeam = 1;
	this.doTraining("waiting_for_more_players");

	this.testObj.buildGameJoinClickHandler(this.gameId, expectedTeam)();

	verify(this.ajax).call("addPlayer", allOf(
		hasMember("gameId", this.gameId),
		hasMember("team", expectedTeam),
		hasMember("playerId", this.playerId)
	));
};

GameListElementBuilderTest.prototype.testSuccessfulJoinGameResponseRefreshesGameListView = function() {
	var testHarness = this;
	var hasCalledAsync = false;
	setTimeout = function(func, time, lang) {
		verify(testHarness.viewManager, never()).showView("gameList");
		func();
		hasCalledAsync = true;
		verify(testHarness.viewManager).showView("gameList");
	};

	this.ajax = new TEST.FakeAjax();
	this.buildTestObj();

	this.team = [this.team[0], [this.team[1][1]]];
	var expectedTeam = 1;
	this.doTraining("waiting_for_more_players");

	this.testObj.buildGameJoinClickHandler(this.gameId, expectedTeam)();
	this.ajax.resolveCall({"success" : true});

	assertTrue(hasCalledAsync);
};

GameListElementBuilderTest.prototype.testHandleShowGameDataCallsViewManager = function() {
	this.testObj.buildShowGameDataHandler(this.gameId)();
	verify(this.viewManager).showView("gamePlay", hasMember("gameId", this.gameId));
};