GamePlayViewTest = TestCase("GamePlayViewTest");

GamePlayViewTest.prototype.setUp = function() {
	this.playerId = "12345";
	this.currentPlayerId = this.playerId;
	this.dealerId = "098765";
	this.ajax = mock(AVOCADO.Ajax);
	this.templateRenderer = mock(AVOCADO.TemplateRenderer);
	this.gamePlayDiv = mock(TEST.FakeJQueryElement);
	this.viewManager = mock(AVOCADO.ViewManager);
	this.locStrings = {"yourTurn" : "Your turn", "otherTurn" : "Other turn %playerId%"};
	this.trumpSelectionAreaBuilder = mock(AVOCADO.TrumpSelectionAreaBuilder);
	this.jqueryWrapper = mock(AVOCADO.JQueryWrapper);
	this.buildTestObj();
};

GamePlayViewTest.prototype.testInitRegistersWithViewManager = function() {
	this.testObj.init();
	verify(this.viewManager).registerView("gamePlay", this.testObj);
};

GamePlayViewTest.prototype.testShowCallsAjaxCorrectly = function() {
	var gameId = "5678";
	this.testObj.show({"gameId" : gameId});
	verify(this.ajax).call("getGameData", allOf(hasMember("playerId", equalTo(this.playerId)), hasMember("gameId", equalTo(gameId))), func());
};

GamePlayViewTest.prototype.testShowRendersResponseCorrectly = function() {
	var gameId = "34827";
	var hand = [{"suit" : 2, "value" : 8}, {"suit" : 3, "value" : 10}, {"suit" : 1, "value" : 12}];
	var upCard = {"suit" : 4, "value" : 12};
	var status = "awesome status";
	var response = {"gameId" : gameId, "hand" : hand, "currentPlayerId" : this.currentPlayerId, "upCard" : upCard, "status" : status, "dealerId" : this.dealerId};
	
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

	var viewGameListElement = mock(TEST.FakeJQueryElement);
	when(this.gamePlayDiv).find(".viewGameList").thenReturn(viewGameListElement);

	var trumpSelectionElement = mock(TEST.FakeJQueryElement);
	when(this.trumpSelectionAreaBuilder).buildTrumpSelectionArea(allOf(hasMember("suit", upCard.suit), hasMember("value", upCard.value)), equalTo(status), equalTo(gameId), equalTo(this.dealerId), equalTo(this.currentPlayerId)).thenReturn(trumpSelectionElement);

	var gameHtml = "the whole game";
	when(this.templateRenderer).renderTemplate("game", allOf(hasMember("gameId", gameId), hasMember("hand", handHtml), hasMember("turn", this.locStrings.yourTurn))).thenReturn(gameHtml);
	var gameElement = mock(TEST.FakeJQueryElement);
	when(this.jqueryWrapper).getElement(gameHtml).thenReturn(gameElement);
	var insertionDivElement = mock(TEST.FakeJQueryElement);
	when(gameElement).find(".trumpSelection").thenReturn(insertionDivElement);

	this.testObj.show({"gameId" : gameId});

	verify(this.gamePlayDiv).empty();
	verify(insertionDivElement).append(trumpSelectionElement);
	verify(this.gamePlayDiv).append(gameElement);
	verify(viewGameListElement).click(this.testObj.handleViewGameListClick);
	verify(this.gamePlayDiv).show();
};

GamePlayViewTest.prototype.testHandlesOtherTurn = function() {
	var gameId = "34827";
	var otherPlayerId = "4320987";
	var hand = [{"suit" : 2, "value" : 8}, {"suit" : 3, "value" : 10}, {"suit" : 1, "value" : 12}];
	var upCard = {"suit" : 4, "value" : 12};
	var response = {"gameId" : gameId, "hand" : hand, "currentPlayerId" : otherPlayerId, "upCard" : upCard, "dealerId" : this.dealerId};
	var expectedTurn = this.locStrings.otherTurn.replace("%playerId%", otherPlayerId);

	this.ajax = new TEST.FakeAjax();
	this.ajax.callbackResponse = response;
	this.buildTestObj();

	var viewGameListElement = mock(TEST.FakeJQueryElement);
	when(this.gamePlayDiv).find(".viewGameList").thenReturn(viewGameListElement);

	var gameHtml = "the whole game";
	when(this.templateRenderer).renderTemplate("game", allOf(hasMember("gameId", gameId), hasMember("hand", anything()), hasMember("turn", expectedTurn))).thenReturn(gameHtml);
	var gameElement = mock(TEST.FakeJQueryElement);
	when(this.jqueryWrapper).getElement(gameHtml).thenReturn(gameElement);
	var insertionDivElement = mock(TEST.FakeJQueryElement);
	when(gameElement).find(".trumpSelection").thenReturn(insertionDivElement);

	this.testObj.show({"gameId" : gameId});

	verify(this.gamePlayDiv).append(gameElement);
};

GamePlayViewTest.prototype.testHideHidesDiv = function() {
	this.testObj.hide();
	verify(this.gamePlayDiv).hide();
};

GamePlayViewTest.prototype.testClickHandlerCallsViewManager = function() {
	this.testObj.handleViewGameListClick();
	verify(this.viewManager).showView("gameList");
};

GamePlayViewTest.prototype.buildTestObj = function() {
	this.testObj = new AVOCADO.GamePlayView(this.ajax, this.playerId, this.templateRenderer, this.gamePlayDiv, this.viewManager, this.locStrings, this.trumpSelectionAreaBuilder, this.jqueryWrapper);
};
