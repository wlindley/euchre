GameListViewTest = TestCase("GameListViewTest")

GameListViewTest.prototype.setUp = function() {
	this.ajax = TEST.FakeAjax.getInstance();
	this.gameLister = AVOCADO.GameLister.getInstance("12345", this.ajax);
	this.templateRenderer = mock(AVOCADO.TemplateRenderer);
	this.gameListDiv = mock(TEST.FakeJQueryElement);
	this.testObj = new AVOCADO.GameListView(this.gameLister, this.templateRenderer, this.gameListDiv);
};

GameListViewTest.prototype.testShowDisplayCorrectHtml = function() {
	var gameEntryBase = "game ";
	var gameIds = [1, 2, 3];
	var statuses = ["round_in_progress", "waiting_for_more_players", "trump_selection"];
	var playerIdLists = [["1", "2", "3", "4"], ["1", "2"], ["3", "4", "5", "6"]];
	var currentPlayers = ["3", null, "6"];
	var gameList = [];
	for (var i = 0; i < gameIds.length; i++) {
		gameList.push({
			"gameId" : gameIds[i],
			"status" : statuses[i],
			"playerIds" : playerIdLists[i],
			"currentPlayerId" : currentPlayers[i]
		});
	}
	this.ajax.callbackResponse = {"games" : gameList, "success" : true};
	var expectedHtml = "";
	for (var i = 0; i < gameList.length; i++) {
		var expectedValues = allOf(
			hasMember("gameId", equalTo(gameList[i].gameId)),
			hasMember("status", equalTo(gameList[i].status)),
			hasMember("playerIds", equalTo(gameList[i].playerIds)),
			hasMember("currentPlayer", equalTo(gameList[i].currentPlayerId))
		);
		var gameHtml = gameEntryBase + gameList[i].gameId;
		when(this.templateRenderer).renderTemplate("gameListEntry", expectedValues).thenReturn(gameHtml);

		expectedHtml += gameHtml;
	}

	this.testObj.show();

	verify(this.gameListDiv).html(expectedHtml);
	verify(this.gameListDiv).show();
};
