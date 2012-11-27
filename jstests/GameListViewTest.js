GameListViewTest = TestCase("GameListViewTest")

GameListViewTest.prototype.setUp = function() {
	this.ajax = FakeAjax.getInstance();
	this.gameLister = GameLister.getInstance("12345", this.ajax);
	this.templateRenderer = mock(TemplateRenderer);
	this.gameListDiv = mock(FakeJQueryElement);
	this.testObj = new GameListView(this.gameLister, this.templateRenderer, this.gameListDiv);
};

GameListViewTest.prototype.testShowDisplayCorrectHtml = function() {
	var expectedGameList = [{"gameId" : 1}, {"gameId" : 2}, {"gameId" : 3}];
	this.ajax.callbackResponse = {"games" : expectedGameList};
	for (var i = 0; i < expectedGameList.length; i++) {
		when(this.templateRenderer).renderTemplate("gameListEntry", expectedGameList[i]).thenReturn("game " + expectedGameList[i].gameId);
	}

	this.testObj.show();

	verify(this.gameListDiv).html("game 1game 2game 3");
	verify(this.gameListDiv).show();
};
