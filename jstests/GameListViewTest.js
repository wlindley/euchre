GameListViewTest = TestCase("GameListViewTest")

GameListViewTest.prototype.setUp = function() {
	this.jqueryWrapper = mock(AVOCADO.JQueryWrapper);
	this.ajax = TEST.FakeAjax.getInstance();
	this.gameLister = AVOCADO.GameLister.getInstance("12345", this.ajax);
	this.templateRenderer = mock(AVOCADO.TemplateRenderer);
	this.gameListDiv = mock(TEST.FakeJQueryElement);
	this.viewManager = mock(AVOCADO.ViewManager);
	this.testObj = new AVOCADO.GameListView(this.gameLister, this.templateRenderer, this.gameListDiv, this.jqueryWrapper, this.viewManager);
};

GameListViewTest.prototype.testInitRegistersWithViewManager = function() {
	this.testObj.init();
	verify(this.viewManager).registerView("gameList", this.testObj);
};

GameListViewTest.prototype.testShowDisplaysCorrectHtml = function() {
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
	for (var i = 0; i < gameList.length; i++) {
		var expectedValues = allOf(
			hasMember("gameId", equalTo(gameList[i].gameId)),
			hasMember("status", equalTo(gameList[i].status)),
			hasMember("playerIds", equalTo(gameList[i].playerIds)),
			hasMember("currentPlayer", equalTo(gameList[i].currentPlayerId))
		);
		var gameHtml = gameEntryBase + gameList[i].gameId;
		when(this.templateRenderer).renderTemplate("gameListEntry", expectedValues).thenReturn(gameHtml);
		when(this.jqueryWrapper).getElement(gameHtml).thenReturn(elements[i]);
		when(elements[i]).find(".viewGameData").thenReturn(linkElements[i]);
	}

	this.testObj.show();

	verify(this.gameListDiv).empty();
	for (var i = 0; i < gameList.length; i++) {
		verify(elements[i]).appendTo(this.gameListDiv);
		if (gameList[i].status != "waiting_for_more_players") {
			verify(linkElements[i]).click(this.testObj.showGameData);
		} else {
			verify(linkElements[i], never()).click(this.testObj.showGameData);
			verify(elements[i]).removeClass("gameListEntryClickable");
		}
	}

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
