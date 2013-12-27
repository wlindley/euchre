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
	this.turnNameElement = mock(TEST.FakeJQueryElement);
	this.turnElement = mock(TEST.FakeJQueryElement);
	this.namePromises = {};
	this.tableElement = mock(TEST.FakeJQueryElement);
	this.tableDataElements = [];
	this.tableDataNameElements = [];
	this.team0Element = mock(TEST.FakeJQueryElement);
	this.team1Element = mock(TEST.FakeJQueryElement);
	this.playGameElement = mock(TEST.FakeJQueryElement);
	this.joinGameElement = mock(TEST.FakeJQueryElement);
	this.inviteToGameElement = mock(TEST.FakeJQueryElement);
	this.gameOverElement = mock(TEST.FakeJQueryElement);
	this.addRobotsButtonElement = mock(TEST.FakeJQueryElement);
	this.addRobotsModalElement = mock(TEST.FakeJQueryElement);
	this.addRobotsModal = mock(AVOCADO.AddRobotsModal);
	this.addRobotsModalContainerElement = mock(TEST.FakeJQueryElement);

	this.clickEvent = mock(TEST.FakeJQueryEvent);

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
	this.addRobotsModalBuilder = mock(AVOCADO.AddRobotsModalBuilder);

	this.showGameDataFunc = mockFunction();
	this.gameInviteClickHandler = mockFunction();
	this.gameJoinClickHandler = mockFunction();
	this.addRobotsClickHandler = mockFunction();

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
	this.testObj = new AVOCADO.GameListElementBuilder(this.jqueryWrapper, this.templateRenderer, this.locStrings, this.playerNameDirectory, this.facebook, this.ajax, this.viewManager, this.addRobotsModalBuilder);
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

	when(this.element).find(".gameListElementTeams").thenReturn(this.tableElement);
	when(this.element).find(".turn").thenReturn(this.turnElement);
	when(this.element).find(".team0").thenReturn(this.team0Element);
	when(this.element).find(".team1").thenReturn(this.team1Element);
	when(this.element).find(".playGame").thenReturn(this.playGameElement);
	when(this.element).find(".joinGame").thenReturn(this.joinGameElement);
	when(this.element).find(".inviteToGame").thenReturn(this.inviteToGameElement);
	when(this.element).find(".gameOver").thenReturn(this.gameOverElement);
	when(this.element).find(".addRobotsButton").thenReturn(this.addRobotsButtonElement);
	when(this.element).find(".addRobotsModalContainer").thenReturn(this.addRobotsModalContainerElement);
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
	when(this.addRobotsModalBuilder).buildAddRobotsModal(this.team, this.gameId).thenReturn(this.addRobotsModal);
	when(this.addRobotsModal).getElement().thenReturn(this.addRobotsModalElement);
};

GameListElementBuilderTest.prototype.trigger = function(isInvite, requestId) {
	return this.testObj.buildListElement(this.gameData, isInvite, requestId);
};

GameListElementBuilderTest.prototype.triggerAddRobotsClick = function() {
	this.testObj.buildAddRobotsClickHandler(this.addRobotsModal)(this.clickEvent);
};

GameListElementBuilderTest.prototype.testBuildListElementReturnsExpectedObject = function() {
	this.doTraining("round_in_progress");
	assertEquals(this.element, this.trigger(true, undefined));
	verify(this.playGameElement).hide();
	verify(this.joinGameElement).hide();
	verify(this.inviteToGameElement).hide();
	verify(this.gameOverElement).hide();
	verify(this.addRobotsButtonElement).hide();
	verify(this.addRobotsModalContainerElement).append(this.addRobotsModalElement);
};

GameListElementBuilderTest.prototype.testHooksUpTurnNamePromise = function() {
	this.doTraining("trump_selection");
	this.trigger(true, undefined);
	verify(this.namePromises[this.currentPlayerId]).registerForUpdates(this.turnNameElement);
};

GameListElementBuilderTest.prototype.testSetsExpectedStringForNullCurrentPlayer = function() {
	this.currentPlayerId = null;
	this.doTraining("round_in_progress");
	this.trigger(true, undefined);
	verify(this.turnNameElement).text(this.locStrings["n/a"]);
};

GameListElementBuilderTest.prototype.testHooksUpTeamNamePromisesAndCTAsAndShowsAddRobotsButtonAndHooksUpAddRobotsClickHandler = function() {
	this.testObj.buildGameInviteClickHandler = mockFunction();
	when(this.testObj.buildGameInviteClickHandler)(this.gameId).thenReturn(this.gameInviteClickHandler);
	this.testObj.buildAddRobotsClickHandler = mockFunction();
	when(this.testObj.buildAddRobotsClickHandler)(this.addRobotsModal).thenReturn(this.addRobotsClickHandler);
	this.team = [this.team[0], [this.team[1][0]]];
	this.doTraining("waiting_for_more_players");
	this.trigger(true, undefined);
	for (var j = 0; j < 2; j++) {
		for (var k = 0; k < 2; k++) {
			if ((j in this.team) && (k in this.team[j])) {
				var pid = this.team[j][k];
				verify(this.namePromises[pid]).registerForUpdates(this.tableDataNameElements[j][k]);
			} else {
				verify(this.tableDataNameElements[j][k]).text(this.locStrings["inviteCTA"]);
			}
		}
	}
	verify(this.addRobotsButtonElement).show();
	verify(this.addRobotsButtonElement).click(this.addRobotsClickHandler);
};

GameListElementBuilderTest.prototype.testHooksUpTeamNamePromisesAndCTAsForJoiningAndDoesNotShowAddRobotsButton = function() {
	var requestId = "230948d_da03983";
	this.testObj.buildGameJoinClickHandler = mockFunction();
	var gameJoinClickHandlers = [[], []];
	for (var j = 0; j < 2; j++) {
		for (var k = 0; k < 2; k++) {
			gameJoinClickHandlers[j][k] = mockFunction();
			when(this.testObj.buildGameJoinClickHandler)(this.gameId, j, requestId).thenReturn(gameJoinClickHandlers[j][k]);
		}
	}
	this.team = [this.team[0], [this.team[1][1]]];
	this.doTraining("waiting_for_more_players");
	this.trigger(false, requestId);
	for (var j = 0; j < 2; j++) {
		for (var k = 0; k < 2; k++) {
			if ((j in this.team) && (k in this.team[j])) {
				var pid = this.team[j][k];
				verify(this.namePromises[pid]).registerForUpdates(this.tableDataNameElements[j][k]);
			} else {
				verify(this.tableDataNameElements[j][k]).text(this.locStrings["joinCTA"]);
				verify(this.tableDataElements[j][k]).click(gameJoinClickHandlers[j][k]);
			}
		}
	}
	verify(this.addRobotsButtonElement, never()).show();
};

GameListElementBuilderTest.prototype.testHooksUpCorrectClickHandler = function() {
	this.testObj.buildShowGameDataHandler = mockFunction();
	when(this.testObj.buildShowGameDataHandler)(this.gameId).thenReturn(this.showGameDataFunc);

	this.doTraining("round_in_progress");
	this.trigger(true, undefined);
	verify(this.element).click(this.showGameDataFunc);
	verify(this.element, never()).click(this.gameInviteClickHandler);
	verify(this.element, never()).click(this.gameJoinClickHandler);
};

GameListElementBuilderTest.prototype.testHooksUpCorrectClickHandlerIfGameNotStartedAndTypeIsInvite = function() {
	this.testObj.buildGameInviteClickHandler = mockFunction();
	when(this.testObj.buildGameInviteClickHandler)(this.gameId).thenReturn(this.gameInviteClickHandler);

	this.currentPlayerId = null;
	this.doTraining("waiting_for_more_players");
	this.trigger(true, undefined);
	verify(this.element, never()).click(this.showGameDataFunc);
	verify(this.element).click(this.gameInviteClickHandler);
	verify(this.element, never()).click(this.gameJoinClickHandler);
	verify(this.inviteToGameElement).show();
};

GameListElementBuilderTest.prototype.testHooksUpCorrectClickHandlerIfGameNotStartedAndTypeIsJoin = function() {
	this.team = [[this.team[0][1]], [this.team[1][1]]];

	var requestId = "230948d_da03983";
	this.testObj.buildGameJoinClickHandler = mockFunction();
	when(this.testObj.buildGameJoinClickHandler)(this.gameId, between(0).and(1), requestId).thenReturn(this.gameJoinClickHandler);

	this.currentPlayerId = null;
	this.doTraining("waiting_for_more_players");
	this.trigger(false, requestId);
	verify(this.element, never()).click(this.showGameDataFunc);
	verify(this.element, never()).click(this.gameInviteClickHandler);
	verify(this.element).click(this.gameJoinClickHandler);
	verify(this.joinGameElement).show();
};

GameListElementBuilderTest.prototype.testHooksUpCorrectClickHandlerIfGameNotStartedAndTypeIsJoinAndOnlyOneSpotOpen = function() {
	this.team = [this.team[0], [this.team[1][1]]];

	var requestId = "230948d_da03983";
	this.testObj.buildGameJoinClickHandler = mockFunction();
	when(this.testObj.buildGameJoinClickHandler)(this.gameId, 1, requestId).thenReturn(this.gameJoinClickHandler);

	this.currentPlayerId = null;
	this.doTraining("waiting_for_more_players");
	this.trigger(false, requestId);
	verify(this.element, never()).click(this.showGameDataFunc);
	verify(this.element, never()).click(this.gameInviteClickHandler);
	verify(this.element).click(this.gameJoinClickHandler);
	verify(this.joinGameElement).show();
};

GameListElementBuilderTest.prototype.testShowsCorrectIconIfCurrentPlayersTurn = function() {
	this.doTraining("round_in_progress");
	this.trigger(true, undefined);
	verify(this.playGameElement).show();
};

GameListElementBuilderTest.prototype.testShowsCorrectIconIfStatusIsGameOver = function() {
	this.currentPlayerId = null;
	this.doTraining("complete");
	this.trigger(true, undefined);
	verify(this.gameOverElement).show();
};

GameListElementBuilderTest.prototype.testShowsCorrectIconIfNotLocalPlayersTurn = function() {
	this.currentPlayerId = this.otherPlayerId;
	this.doTraining("round_in_progress");
	this.trigger(true, undefined);
	verify(this.playGameElement, never()).show();
};

GameListElementBuilderTest.prototype.testAddsCorrectClassesForTeams = function() {
	this.doTraining("round_in_progress");
	this.trigger(true, undefined);
	verify(this.team0Element).addClass("red");
	verify(this.team1Element).addClass("green");
};

GameListElementBuilderTest.prototype.testAddsCorrectClassesForTeamsWhenLocalPlayerIsOnOtherTeam = function() {
	this.team = [this.team[1], this.team[0]];
	this.doTraining("round_in_progress");
	this.trigger(true, undefined);
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
	var requestId = "230948d_da03983";
	this.doTraining("waiting_for_more_players");

	this.testObj.buildGameJoinClickHandler(this.gameId, expectedTeam, requestId)();

	verify(this.ajax).call("addPlayer", allOf(
		hasMember("gameId", this.gameId),
		hasMember("team", expectedTeam),
		hasMember("playerId", this.playerId)
	));
};

GameListElementBuilderTest.prototype.testSuccessfulJoinGameResponseRefreshesGameListViewAndDeletesRequest = function() {
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
	var requestId = "230948d_da03983";
	this.doTraining("waiting_for_more_players");

	this.testObj.buildGameJoinClickHandler(this.gameId, expectedTeam, requestId)();
	this.ajax.resolveCall({"success" : true});

	verify(this.facebook).deleteAppRequest(requestId);
	assertTrue(hasCalledAsync);
};

GameListElementBuilderTest.prototype.testFailedJoinGameResponseDoesNotDeleteRequest = function() {
	this.ajax = new TEST.FakeAjax();
	this.buildTestObj();

	this.team = [this.team[0], [this.team[1][1]]];
	var expectedTeam = 1;
	var requestId = "230948d_da03983";
	this.doTraining("waiting_for_more_players");

	this.testObj.buildGameJoinClickHandler(this.gameId, expectedTeam, requestId)();
	this.ajax.resolveCall({"success" : false});

	verify(this.facebook, never()).deleteAppRequest(requestId);
};

GameListElementBuilderTest.prototype.testHandleShowGameDataCallsViewManager = function() {
	this.testObj.buildShowGameDataHandler(this.gameId)();
	verify(this.viewManager).showView("gamePlay", hasMember("gameId", this.gameId));
};

GameListElementBuilderTest.prototype.testAddRobotsClickHandlerStopsEventPropagation = function() {
	this.team = [this.team[0], [this.team[1][0]]];
	this.doTraining("waiting_for_more_players");
	this.triggerAddRobotsClick();
	verify(this.clickEvent).stopPropagation();
};

GameListElementBuilderTest.prototype.testAddRobotsClickHandlerShowsModalDialog = function() {
	this.team = [this.team[0], [this.team[1][0]]];
	this.doTraining("waiting_for_more_players");
	this.triggerAddRobotsClick();
	verify(this.addRobotsModal).show();
};