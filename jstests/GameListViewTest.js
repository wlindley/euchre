GameListViewTest = TestCase("GameListViewTest")

DivObject = function() {
	this.html = function() {};
	this.show = function() {};
};

GameListViewTest.prototype.setUp = function() {
	this.ajax = FakeAjax.getInstance();
	this.gameLister = GameLister.getInstance("12345", this.ajax);
	this.gameListHtmlBuilder = mock(GameListHtmlBuilder);
	this.gameListDiv = mock(DivObject);
	this.testObj = GameListView.getInstance(this.gameLister, this.gameListHtmlBuilder, this.gameListDiv);
};

GameListViewTest.prototype.testShowDisplayCorrectHtml = function() {
	var expectedGameList = "a list of games";
	this.ajax.callbackResponse = expectedGameList;
	var gameListHtml = "game list HTML";
	when(this.gameListHtmlBuilder).buildHtml(expectedGameList).thenReturn(gameListHtml);

	this.testObj.show();

	verify(this.gameListDiv).html(gameListHtml);
	verify(this.gameListDiv).show();
};
