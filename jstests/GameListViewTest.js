GameListViewTest = TestCase("GameListViewTest")

GameListViewTest.prototype.setUp = function() {
	this.jqueryWrapper = mock(AVOCADO.JQueryWrapper);
	this.ajax = TEST.FakeAjax.getInstance();
	this.gameLister = AVOCADO.GameLister.getInstance("12345", this.ajax);
	this.templateRenderer = mock(AVOCADO.TemplateRenderer);
	this.gameListDiv = mock(TEST.FakeJQueryElement);
	this.viewManager = mock(AVOCADO.ViewManager);

	this.gameCreator = mock(AVOCADO.GameCreator);
	this.gameJoiner = mock(AVOCADO.GameJoiner);
	this.prevGameJoinerGetFunc = AVOCADO.GameJoiner.getInstance;

	this.locStrings = {"yourTurn" : "your turn", "otherTurn" : "Player %playerId%'s turn", "noTurn" : "no turn"};
	this.playerId = "3";
	this.testObj = new AVOCADO.GameListView(this.gameLister, this.templateRenderer, this.gameListDiv, this.jqueryWrapper, this.viewManager, this.ajax, this.locStrings, this.playerId, this.gameCreator);
};

GameListViewTest.prototype.tearDown = function() {
	AVOCADO.GameJoiner.getInstance = this.prevGameJoinerGetFunc;
};

GameListViewTest.prototype.testInitRegistersWithViewManager = function() {
	this.testObj.init();
	verify(this.viewManager).registerView("gameList", this.testObj);
};

GameListViewTest.prototype.testShowDisplaysCorrectHtml = function() {
	//data
	var gameEntryBase = "game ";
	var gameIds = [1, 2, 3];
	var statuses = ["round_in_progress", "waiting_for_more_players", "trump_selection"];
	var playerIdLists = [["1", "2", "3", "4"], ["1", "2"], ["3", "4", "5", "6"]];
	var currentPlayers = ["3", null, "6"];
	var gameList = [];
	var elements = [];
	var linkElements = [];
	for (var i = 0; i < gameIds.length; i++) {
		gameList.push({
			"gameId" : gameIds[i],
			"status" : statuses[i],
			"playerIds" : playerIdLists[i],
			"currentPlayerId" : currentPlayers[i]
		});
		elements.push(mock(TEST.FakeJQueryElement));
		linkElements.push(mock(TEST.FakeJQueryElement));
	}
	this.ajax.callbackResponse = {"games" : gameList, "success" : true};

	//training
	for (var i = 0; i < gameList.length; i++) {
		var expectedTurnString = this.locStrings.yourTurn;
		if (null == currentPlayers[i]) {
			expectedTurnString = this.locStrings.noTurn;
		} else if (currentPlayers[i] != this.playerId) {
			expectedTurnString = this.locStrings.otherTurn.replace("%playerId%", currentPlayers[i]);
		}
		var expectedValues = allOf(
			hasMember("gameId", equalTo(gameList[i].gameId)),
			hasMember("status", equalTo(gameList[i].status)),
			hasMember("playerIds", equalTo(gameList[i].playerIds)),
			hasMember("turn", equalTo(expectedTurnString))
		);
		var gameHtml = gameEntryBase + gameList[i].gameId;
		when(this.templateRenderer).renderTemplate("gameListEntry", expectedValues).thenReturn(gameHtml);
		when(this.jqueryWrapper).getElement(gameHtml).thenReturn(elements[i]);
		when(elements[i]).find(".viewGameData").thenReturn(linkElements[i]);
	}

	//train game creator
	/*var gameCreatorHtml = "game creator";
	when(this.templateRenderer).renderTemplate("gameCreator").thenReturn(gameCreatorHtml);
	var gameCreatorElement = mock(TEST.FakeJQueryElement);
	when(this.jqueryWrapper).getElement(gameCreatorHtml).thenReturn(gameCreatorElement);
	var createGameButton = mock(TEST.FakeJQueryElement);
	when(gameCreatorElement).find("#btnCreateGame").thenReturn(createGameButton);
	AVOCADO.GameCreator.getInstance = mockFunction();
	when(AVOCADO.GameCreator.getInstance)(this.playerId, this.ajax, createGameButton, this.viewManager).thenReturn(this.gameCreator);*/
	var gameCreatorElement = mock(TEST.FakeJQueryElement);
	when(this.gameCreator).buildGameCreator().thenReturn(gameCreatorElement);

	//train game joiner
	var gameJoinHtml = "game joiner";
	when(this.templateRenderer).renderTemplate("gameJoiner").thenReturn(gameJoinHtml);
	var gameJoinerElement = mock(TEST.FakeJQueryElement);
	when(this.jqueryWrapper).getElement(gameJoinHtml).thenReturn(gameJoinerElement);
	var gameIdInput = mock(TEST.FakeJQueryElement);
	var teamIdInput = mock(TEST.FakeJQueryElement);
	var joinButton = mock(TEST.FakeJQueryElement);
	when(gameJoinerElement).find("#txtGameId").thenReturn(gameIdInput);
	when(gameJoinerElement).find("#txtTeam").thenReturn(teamIdInput);
	when(gameJoinerElement).find("#btnJoinGame").thenReturn(joinButton);
	AVOCADO.GameJoiner.getInstance = mockFunction();
	when(AVOCADO.GameJoiner.getInstance)(this.playerId, this.ajax, gameIdInput, teamIdInput, joinButton, this.viewManager).thenReturn(this.gameJoiner);

	//trigger
	this.testObj.show();

	//verification
	verify(this.gameListDiv).empty();
	for (var i = 0; i < gameList.length; i++) {
		verify(elements[i]).appendTo(this.gameListDiv);
		if (gameList[i].status != "waiting_for_more_players") {
			verify(linkElements[i]).click(this.testObj.showGameData);
		} else {
			verify(linkElements[i], never()).click(this.testObj.showGameData);
			verify(elements[i]).removeClass("gameListEntryClickable");
		}
		if (currentPlayers[i] != this.playerId) {
			verify(elements[i]).removeClass("gameListEntryYourTurn");
		}
	}
	verify(this.gameListDiv).append(gameCreatorElement);
	verify(this.gameListDiv).append(gameJoinerElement);
	verify(this.gameJoiner).init();

	verify(this.gameListDiv).show();
};

GameListViewTest.prototype.testShowGameDataHidesSelfAndCallsGamePlayView = function() {
	var gameId = "984632";
	var jqElement = mock(TEST.FakeJQueryElement);
	var htmlElement = "some html element";
	when(this.jqueryWrapper).getElement(htmlElement).thenReturn(jqElement);
	when(jqElement).attr("id").thenReturn("gameId_" + gameId);
	var event = {"currentTarget" : htmlElement};

	this.testObj.showGameData(event);

	verify(this.gameListDiv).hide();
	verify(this.viewManager).showView("gamePlay", hasMember("gameId", gameId));
};

GameListViewTest.prototype.testHideHidesDiv = function() {
	this.testObj.hide();
	verify(this.gameListDiv).hide();
};
