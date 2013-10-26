GameListViewTest2 = TestCase("GameListViewTest2");

GameListViewTest2.prototype.setUp = function() {
	this.playerId = "45678ghi";
	this.locStrings = {
		"yourTurn" : "your turn",
		"otherTurn" : "Player %playerId%'s turn",
		"noTurn" : "no turn"
	};

	this.ajax = TEST.FakeAjax.getInstance();
	this.gameLister = AVOCADO.GameLister.getInstance(this.playerId, this.ajax);

	this.templateRenderer = mock(AVOCADO.TemplateRenderer);
	this.jqueryWrapper = mock(AVOCADO.JQueryWrapper);
	this.viewManager = mock(AVOCADO.ViewManager);
	this.gameCreatorBuilder = mock(AVOCADO.GameCreatorBuilder);
	this.gameJoinerBuilder = mock(AVOCADO.GameJoinerBuilder);

	this.gameListDiv = mock(TEST.FakeJQueryElement);

	this.gameIds = [1, 2, 3];
	this.statuses = ["round_in_progress", "waiting_for_more_players", "trump_selection"];
	this.playerIdLists = [["2345", "3456", this.playerId, "1234"], [this.playerId, "2345"], [this.playerId, "1234", "0987", "9876"]];
	this.currentPlayerIds = [this.playerId, null, "9876"];
	this.gameList = [];
	this.elements = [];
	this.linkElements = [];
	for (var i in this.gameIds) {
		this.gameList.push({
			"gameId" : this.gameIds[i],
			"status" : this.statuses[i],
			"playerIds" : this.playerIdLists[i],
			"currentPlayerId" : this.currentPlayerIds[i]
		});
		this.elements.push(mock(TEST.FakeJQueryElement));
		this.linkElements.push(mock(TEST.FakeJQueryElement));
	}
	this.listHeaderHtml = "list header";
	this.gameCreatorElement = mock(TEST.FakeJQueryElement);
	this.gameJoinerElement = mock(TEST.FakeJQueryElement);

	this.clickTargetHtml = "click target html";
	this.clickTargetElement = mock(TEST.FakeJQueryElement);
	this.clickTargetGameId = 2345;
	this.clickEvent = {"currentTarget" : this.clickTargetHtml};

	this.buildTestObj();
	this.doTraining();
};

GameListViewTest2.prototype.buildTestObj = function() {
	this.testObj = new AVOCADO.GameListView(this.gameLister, this.templateRenderer, this.gameListDiv, this.jqueryWrapper, this.viewManager, this.ajax, this.locStrings, this.playerId, this.gameCreatorBuilder, this.gameJoinerBuilder);
};

GameListViewTest2.prototype.doTraining = function() {
	this.ajax.callbackResponse = {"games" : this.gameList, "success" : true};

	when(this.templateRenderer).renderTemplate("gameListHeader").thenReturn(this.listHeaderHtml);
	for (var i in this.gameList) {
		var expectedTurnString = this.locStrings["yourTurn"];
		if (null == this.currentPlayerIds[i]) {
			expectedTurnString = this.locStrings["noTurn"];
		} else if (this.currentPlayerIds[i] != this.playerId) {
			expectedTurnString = this.locStrings["otherTurn"].replace("%playerId%", this.currentPlayerIds[i]);
		}
		var gameHtml = "game " + this.gameIds[i];
		var expectedValues = allOf(
			hasMember("gameId", equalTo(this.gameIds[i])),
			hasMember("status", equalTo(this.statuses[i])),
			hasMember("playerIds", equalTo(this.playerIdLists[i])),
			hasMember("turn", equalTo(expectedTurnString))
		);
		when(this.templateRenderer).renderTemplate("gameListEntry", expectedValues).thenReturn(gameHtml);
		when(this.jqueryWrapper).getElement(gameHtml).thenReturn(this.elements[i]);
		when(this.elements[i]).find(".viewGameData").thenReturn(this.linkElements[i]);
	}

	when(this.gameCreatorBuilder).buildGameCreator().thenReturn(this.gameCreatorElement);
	when(this.gameJoinerBuilder).buildGameJoiner().thenReturn(this.gameJoinerElement);

	when(this.jqueryWrapper).getElement(this.clickTargetHtml).thenReturn(this.clickTargetElement);
	when(this.clickTargetElement).attr("id").thenReturn("gameId_" + this.clickTargetGameId);
};

GameListViewTest2.prototype.trigger = function() {
	this.testObj.show();
};

GameListViewTest2.prototype.testInitRegistersWithViewManager = function() {
	this.testObj.init();
	verify(this.viewManager).registerView("gameList", this.testObj);
};

GameListViewTest2.prototype.testShowEmptiesContainerDiv = function() {
	this.trigger();
	verify(this.gameListDiv).empty();
};

GameListViewTest2.prototype.testShowAppendsHeader = function() {
	this.trigger();
	verify(this.gameListDiv).append(this.listHeaderHtml);
};

GameListViewTest2.prototype.testShowAppendsGameListElements = function() {
	this.trigger();
	for (var i in this.elements) {
		verify(this.elements[i]).appendTo(this.gameListDiv);
	}
};

GameListViewTest2.prototype.testShowAppendsGameCreator = function() {
	this.trigger();
	verify(this.gameListDiv).append(this.gameCreatorElement);
};

GameListViewTest2.prototype.testShowAppendsGameJoiner = function() {
	this.trigger();
	verify(this.gameListDiv).append(this.gameJoinerElement);
};

GameListViewTest2.prototype.testShowCallsShowOnContainerDiv = function() {
	this.trigger();
	verify(this.gameListDiv).show();
};

GameListViewTest2.prototype.testShowEmptiesContainerDivBeforeAppendingHeader = function() {
	when(this.gameListDiv).empty().thenThrow("expected exception");
	var hadException = false;

	try {
		this.trigger();
	} catch (ex) {
		hadException = true;
	}

	assertTrue(hadException);
	verify(this.gameListDiv).empty();
	verify(this.gameListDiv, never()).append(anything());
};

GameListViewTest2.prototype.testShowHooksUpCorrectClickHandlers = function() {
	this.trigger();
	for (var i in this.statuses) {
		if ("waiting_for_more_players" != this.statuses[i]) {
			verify(this.linkElements[i]).click(this.testObj.showGameData);
		} else {
			verify(this.linkElements[i], never()).click(this.testObj.showGameData);
		}
	}
};

GameListViewTest2.prototype.testShowRemovesClassesFromListEntries = function() {
	this.trigger();
	for (var i in this.statuses) {
		if ("waiting_for_more_players" == this.statuses[i]) {
			verify(this.elements[i]).removeClass("gameListEntryClickable");
		}
		if (this.currentPlayerIds[i] != this.playerId) {
			verify(this.elements[i]).removeClass("gameListEntryYourTurn");
		}
	}
};

GameListViewTest2.prototype.testShowGameDataHidesSelf = function() {
	this.testObj.showGameData(this.clickEvent);
	verify(this.gameListDiv).hide();
}

GameListViewTest2.prototype.testShowGameDataCallsGamePlayView = function() {
	this.testObj.showGameData(this.clickEvent);
	verify(this.viewManager).showView("gamePlay", hasMember("gameId", this.clickTargetGameId));
};

GameListViewTest2.prototype.testHideHidesContainerDiv = function() {
	this.testObj.hide();
	verify(this.gameListDiv).hide();
};