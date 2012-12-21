GamePlayViewTest = TestCase("GamePlayViewTest");

GamePlayViewTest.prototype.setUp = function() {
	this.playerId = "12345";
	this.ajax = mock(AVOCADO.Ajax);
	this.templateRenderer = mock(AVOCADO.TemplateRenderer);
	this.gamePlayDiv = mock(TEST.FakeJQueryElement);
	this.buildTestObj();
};

GamePlayViewTest.prototype.testShowCallsAjaxCorrectly = function() {
	var gameId = "5678";
	this.testObj.show(gameId);
	verify(this.ajax).call("getGameData", allOf(hasMember("playerId", equalTo(this.playerId)), hasMember("gameId", equalTo(gameId))), func());
};

GamePlayViewTest.prototype.testShowRendersResponseCorrectly = function() {
	var gameId = "34827";
	var hand = [{"suit" : 2, "value" : 8}, {"suit" : 3, "value" : 10}, {"suit" : 1, "value" : 12}];
	var response = {"gameId" : gameId, "hand" : hand};
	
	this.ajax = new TEST.FakeAjax();
	this.ajax.callbackResponse = response;
	this.buildTestObj();

	var cardHtmls = [];
	var completeCardHtml = "";
	for (var i = 0; i < hand.length; i++) {
		var curHtml = "card " + i;
		cardHtmls.push(curHtml);
		when(this.templateRenderer).renderTemplate("card", allOf(hasMember("suit", hand[i].suit), hasMember("value", hand[i].value))).thenReturn(curHtml);
		completeCardHtml += curHtml;
	}
	
	var handHtml = "the whole hand";
	when(this.templateRenderer).renderTemplate("hand", hasMember("hand", completeCardHtml)).thenReturn(handHtml);

	var gameHtml = "the whole game";
	when(this.templateRenderer).renderTemplate("game", allOf(hasMember("gameId", gameId), hasMember("hand", handHtml))).thenReturn(gameHtml);

	this.testObj.show(gameId);

	verify(this.gamePlayDiv).html(gameHtml);
	verify(this.gamePlayDiv).show();
};

GamePlayViewTest.prototype.buildTestObj = function() {
	this.testObj = new AVOCADO.GamePlayView(this.ajax, this.playerId, this.templateRenderer, this.gamePlayDiv);
};
