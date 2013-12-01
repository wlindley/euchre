GameListViewTest = TestCase("GameListViewTest");

GameListViewTest.prototype.setUp = function() {
	this.ajax = TEST.FakeAjax.getInstance();
	this.templateRenderer = mock(AVOCADO.TemplateRenderer);
	this.jqueryWrapper = mock(AVOCADO.JQueryWrapper);
	this.viewManager = mock(AVOCADO.ViewManager);
	this.gameCreatorBuilder = mock(AVOCADO.GameCreatorBuilder);
	this.facebook = mock(AVOCADO.Facebook);
	this.gameLister = AVOCADO.GameLister.getInstance(this.facebook, this.ajax);
	this.gameListElementBuilder = mock(AVOCADO.GameListElementBuilder);

	this.gameListDiv = mock(TEST.FakeJQueryElement);
	this.gameListElement = mock(TEST.FakeJQueryElement);

	this.playerId = "45678ghi";
	this.gameId = "14klj234";
	this.status = "round_in_progress";
	this.teams = [["2345", "3456"], [this.playerId, "1234"]];
	this.currentPlayerIds = this.playerId;
	this.gameData = {
		"gameId" : this.gameId,
		"status" : this.status,
		"teams" : this.teams,
		"currentPlayerId" : this.currentPlayerId
	};
	this.listHeaderHtml = "list header";
	this.gameCreatorElement = mock(TEST.FakeJQueryElement);
	this.gameListMenuElement = mock(TEST.FakeJQueryElement);
	this.gameListMenuHtml = "game list menu html";
	this.gameCreatorInsertionElement = mock(TEST.FakeJQueryElement);

	this.clickTargetHtml = "click target html";
	this.clickTargetElement = mock(TEST.FakeJQueryElement);
	this.clickTargetGameId = 2345;
	this.clickEvent = {"currentTarget" : this.clickTargetHtml};

	this.ajaxResponse = {"games" : [this.gameData], "success" : true};

	this.buildTestObj();
	this.doTraining();
};

GameListViewTest.prototype.buildTestObj = function() {
	this.testObj = new AVOCADO.GameListView(this.gameLister, this.templateRenderer, this.gameListDiv, this.jqueryWrapper, this.viewManager, this.gameCreatorBuilder, this.gameListElementBuilder);
};

GameListViewTest.prototype.doTraining = function() {
	when(this.facebook).getSignedInPlayerId().thenReturn(this.playerId);

	when(this.templateRenderer).renderTemplate("gameListHeader").thenReturn(this.listHeaderHtml);
	when(this.gameListElementBuilder).buildListElement(allOf(
		hasMember("gameId", this.gameId),
		hasMember("status", this.status),
		hasMember("teams", this.teams),
		hasMember("currentPlayerId", this.currentPlayerId)
	), this.testObj.showGameData, true).thenReturn(this.gameListElement);

	when(this.gameCreatorBuilder).buildGameCreator().thenReturn(this.gameCreatorElement);

	when(this.templateRenderer).renderTemplate("gameListMenu").thenReturn(this.gameListMenuHtml);
	when(this.jqueryWrapper).getElement(this.gameListMenuHtml).thenReturn(this.gameListMenuElement);
	when(this.gameListMenuElement).find(".gameCreatorContainer").thenReturn(this.gameCreatorInsertionElement);

	when(this.jqueryWrapper).getElement(this.clickTargetHtml).thenReturn(this.clickTargetElement);
	when(this.clickTargetElement).attr("id").thenReturn("gameId_" + this.clickTargetGameId);
};

GameListViewTest.prototype.trigger = function() {
	this.testObj.show();
	this.ajax.resolveCall(this.ajaxResponse);
};

GameListViewTest.prototype.testInitRegistersWithViewManager = function() {
	this.testObj.init();
	verify(this.viewManager).registerView("gameList", this.testObj);
};

GameListViewTest.prototype.testShowEmptiesContainerDiv = function() {
	this.trigger();
	verify(this.gameListDiv).empty();
};

GameListViewTest.prototype.testShowAppendsHeader = function() {
	this.trigger();
	verify(this.gameListDiv).append(this.listHeaderHtml);
};

GameListViewTest.prototype.testShowAppendsGameListElements = function() {
	this.trigger();
	verify(this.gameListElement).appendTo(this.gameListDiv);
};

GameListViewTest.prototype.testShowAppendsFullMenu = function() {
	this.trigger();
	verify(this.gameListDiv).append(this.gameListMenuElement);
	verify(this.gameCreatorInsertionElement).append(this.gameCreatorElement);
};

GameListViewTest.prototype.testShowCallsShowOnContainerDiv = function() {
	this.trigger();
	verify(this.gameListDiv).show();
};

GameListViewTest.prototype.testShowEmptiesContainerDivBeforeAppendingHeader = function() {
	when(this.gameListDiv).empty().thenThrow("expected exception");

	try {
		this.trigger();
	} catch (ex) {
		//intentionally empty
	}

	verify(this.gameListDiv).empty();
	verify(this.gameListDiv, never()).append(anything());
};

GameListViewTest.prototype.testShowAppendsHeaderBeforeListElements = function() {
	when(this.gameListDiv).append(this.listHeaderHtml).thenThrow("expected exception");

	try {
		this.trigger();
	} catch (ex) {
		//intentionally empty
	}

	verify(this.gameListDiv).append(this.listHeaderHtml);
	verify(this.gameListElement, never()).appendTo(anything());
};

GameListViewTest.prototype.testShowAppendsListElementsBeforeGameCreator = function() {
	when(this.gameListElement).appendTo(this.gameListDiv).thenThrow("expected exception");

	try {
		this.trigger();
	} catch (ex) {
		//intentionally empty
	}

	verify(this.gameListElement).appendTo(this.gameListDiv);
	verify(this.gameListDiv, never()).append(this.gameCreatorElement);
};

GameListViewTest.prototype.testShowGameDataHidesSelf = function() {
	this.testObj.showGameData(this.clickEvent);
	verify(this.gameListDiv).hide();
}

GameListViewTest.prototype.testShowGameDataCallsGamePlayView = function() {
	this.testObj.showGameData(this.clickEvent);
	verify(this.viewManager).showView("gamePlay", hasMember("gameId", this.clickTargetGameId));
};

GameListViewTest.prototype.testHideHidesContainerDiv = function() {
	this.testObj.hide();
	verify(this.gameListDiv).hide();
};