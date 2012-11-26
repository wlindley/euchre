GameListViewTest = TestCase("GameListViewTest")

GameListViewTest.prototype.setUp = function() {
	this.ajax = FakeAjax.getInstance();
	this.gameLister = GameLister.getInstance("12345", this.ajax);
	this.gameListHtmlBuilder = mock(GameListHtmlBuilder);
	this.gameListDiv = mock(FakeJQueryElement);
	this.testObj = new GameListView(this.gameLister, this.gameListHtmlBuilder, this.gameListDiv);
};

GameListViewTest.prototype.testShowDisplayCorrectHtml = function() {
	var expectedGameList = "a list of games";
	this.ajax.callbackResponse = {"games" : expectedGameList};
	var gameListHtml = "game list HTML";
	when(this.gameListHtmlBuilder).buildHtml(expectedGameList).thenReturn(gameListHtml);

	this.testObj.show();

	verify(this.gameListDiv).html(gameListHtml);
	verify(this.gameListDiv).show();
};
