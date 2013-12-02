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
	this.gameInviteLister = mock(AVOCADO.GameInviteLister);

	this.playerId = "45678ghi";

	this.gameId = "14klj234";
	this.status = "round_in_progress";
	this.teams = [["2345", "3456"], [this.playerId, "1234"]];
	this.currentPlayerId = this.playerId;
	this.gameData = {
		"gameId" : this.gameId,
		"status" : this.status,
		"teams" : this.teams,
		"currentPlayerId" : this.currentPlayerId
	};

	this.inviteGameId = "14klj234";
	this.inviteStatus = "round_in_progress";
	this.inviteTeams = [["2345", "3456"], [this.playerId, "1234"]];
	this.inviteCurrentPlayerId = this.playerId;
	this.inviteGameData = {
		"gameId" : this.inviteGameId,
		"status" : this.inviteStatus,
		"teams" : this.inviteTeams,
		"currentPlayerId" : this.inviteCurrentPlayerId
	};

	this.rootElement = mock(TEST.FakeJQueryElement);
	this.gameListHtml = "game list html";
	this.viewElement = mock(TEST.FakeJQueryElement);
	this.gameListDiv = mock(TEST.FakeJQueryElement);

	this.gameListElement = mock(TEST.FakeJQueryElement);
	this.inviteGameListElement = mock(TEST.FakeJQueryElement);

	this.gameCreatorElement = mock(TEST.FakeJQueryElement);
	this.gameListMenuElement = mock(TEST.FakeJQueryElement);
	this.gameCreatorInsertionElement = mock(TEST.FakeJQueryElement);

	this.clickTargetHtml = "click target html";
	this.clickTargetElement = mock(TEST.FakeJQueryElement);
	when(this.clickTargetElement).text().thenReturn("click target element");
	this.clickTargetGameId = "2345";
	this.clickEvent = {"currentTarget" : this.clickTargetHtml};

	this.ajaxResponse = {"games" : [this.gameData], "success" : true};
	this.getGameInviteListPromise = mock(TEST.FakePromise);

	this.buildTestObj();
	this.doTraining();
};

GameListViewTest.prototype.buildTestObj = function() {
	this.testObj = new AVOCADO.GameListView(this.gameLister, this.templateRenderer, this.rootElement, this.jqueryWrapper, this.viewManager, this.gameCreatorBuilder, this.gameListElementBuilder, this.gameInviteLister);
};

GameListViewTest.prototype.doTraining = function() {
	when(this.facebook).getSignedInPlayerId().thenReturn(this.playerId);

	when(this.gameInviteLister).getGameInviteList().thenReturn(this.getGameInviteListPromise);

	when(this.gameListElementBuilder).buildListElement(allOf(
		hasMember("gameId", this.gameId),
		hasMember("status", this.status),
		hasMember("teams", this.teams),
		hasMember("currentPlayerId", this.currentPlayerId)
	), true).thenReturn(this.gameListElement);
	when(this.gameListElementBuilder).buildListElement(allOf(
		hasMember("gameId", this.inviteGameId),
		hasMember("status", this.inviteStatus),
		hasMember("teams", this.inviteTeams),
		hasMember("currentPlayerId", this.inviteCurrentPlayerId)
	), false).thenReturn(this.inviteGameListElement);

	when(this.gameCreatorBuilder).buildGameCreator().thenReturn(this.gameCreatorElement);

	when(this.jqueryWrapper).getElement(this.clickTargetHtml).thenReturn(this.clickTargetElement);
	when(this.clickTargetElement).attr("id").thenReturn("gameId_" + this.clickTargetGameId);

	when(this.templateRenderer).renderTemplate("gameList").thenReturn(this.gameListHtml);
	when(this.jqueryWrapper).getElement().thenReturn(this.viewElement);
	when(this.viewElement).find(".gameListMenu").thenReturn(this.gameListMenuElement);
	when(this.viewElement).find(".gameCreatorContainer").thenReturn(this.gameCreatorInsertionElement);
	when(this.viewElement).find(".gameListContainer").thenReturn(this.gameListDiv);
	when(this.rootElement).find(".gameListContainer").thenReturn(this.gameListDiv);
};

GameListViewTest.prototype.trigger = function() {
	this.testObj.show();
	this.ajax.resolveCall(this.ajaxResponse);
};

GameListViewTest.prototype.testInitRegistersWithViewManager = function() {
	this.testObj.init();
	verify(this.viewManager).registerView("gameList", this.testObj);
};

GameListViewTest.prototype.testShowHooksUpGameInviteListerCallback = function() {
	this.testObj.show();
	verify(this.getGameInviteListPromise).done(this.testObj.handleGameInviteListResponse);
};

GameListViewTest.prototype.testShowEmptiesContainerDiv = function() {
	this.testObj.show();
	verify(this.rootElement).empty();
};

GameListViewTest.prototype.testShowAttachesViewToRootElement = function() {
	this.testObj.show();
	verify(this.rootElement).append(this.viewElement);
};

GameListViewTest.prototype.testShowEmptiesContainerDivBeforeAttachingView = function() {
	when(this.rootElement).empty().thenThrow("expected exception");

	try {
		this.trigger();
	} catch (ex) {
		//intentionally empty
	}

	verify(this.rootElement).empty()
	verify(this.rootElement, never()).append(this.viewElement);
};

GameListViewTest.prototype.testShowInsertsMenuElements = function() {
	this.testObj.show();
	verify(this.gameCreatorInsertionElement).append(this.gameCreatorElement);
};

GameListViewTest.prototype.testShowCallsShowOnContainerDiv = function() {
	this.testObj.show();
	verify(this.rootElement).show();
};

GameListViewTest.prototype.testShowAppendsGameListElements = function() {
	this.trigger();
	verify(this.gameListDiv).append(this.gameListElement);
};

GameListViewTest.prototype.testShowAttachesViewBeforeAppendingGameListElements = function() {
	when(this.rootElement).append(this.viewElement).thenThrow("expected exception");

	try {
		this.trigger();
	} catch (ex) {
		//intentionally empty
	}

	verify(this.rootElement).append(this.viewElement);
	verify(this.gameListDiv, never()).append(anything());
};

GameListViewTest.prototype.testHideHidesContainerDiv = function() {
	this.testObj.hide();
	verify(this.rootElement).hide();
};

GameListViewTest.prototype.testHandleGameInviteListResponsePrependsInvites = function() {
	this.testObj.handleGameInviteListResponse([this.inviteGameData]);
	verify(this.gameListDiv).prepend(this.inviteGameListElement);
};