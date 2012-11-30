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
	var cardBase = "card ";
	var hands = [[{"suit" : 1, "value" : 2}], [{"suit" : 2, "value" : 3}], [{"suit" : 3, "value" : 4}]];
	var gameList = [{"gameId" : 1, "hand" : hands[0]}, {"gameId" : 2, "hand" : hands[1]}, {"gameId" : 3, "hand" : hands[2]}];
	this.ajax.callbackResponse = {"games" : gameList};
	var expectedHtml = "";
	for (var i = 0; i < gameList.length; i++) {
		var handHtml = "";
		for (var j = 0; j < hands[i].length; j++) {
			handHtml += cardBase + hands[i][j].suit + hands[i][j].value;
			when(this.templateRenderer).renderTemplate("card", hands[i][j]).thenReturn(handHtml);
		}

		var expectedValues = allOf(
			hasMember("gameId", equalTo(gameList[i].gameId)),
			hasMember("hand", equalTo(handHtml))
		);
		var gameHtml = gameEntryBase + gameList[i].gameId;
		when(this.templateRenderer).renderTemplate("gameListEntry", expectedValues).thenReturn(gameHtml + handHtml);

		expectedHtml += gameHtml + handHtml;
	}

	this.testObj.show();

	verify(this.gameListDiv).html(expectedHtml);
	verify(this.gameListDiv).show();
};
