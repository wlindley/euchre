GameCompleteDisplayBuilderTest = TestCase("GameCompleteDisplayBuilderTest");

GameCompleteDisplayBuilderTest.prototype.setUp = function() {
	this.origSetTimeout = setTimeout;
	this.setTimeout = function(func, time, lang) {
		func();
	};

	this.buildObjects();
	this.doTraining();
	this.buildTestObj();
};

GameCompleteDisplayBuilderTest.prototype.tearDown = function() {
	setTimeout = this.origSetTimeout;
};

GameCompleteDisplayBuilderTest.prototype.buildObjects = function() {
	this.templateRenderer = mock(AVOCADO.TemplateRenderer);
	this.jqueryWrapper = mock(AVOCADO.JQueryWrapper);
	this.locStrings = {"won" : "won!", "and" : "foo and", "dismiss" : "diss that miss"};
	this.playerNameDirectory = mock(AVOCADO.PlayerNameDirectory);
	this.facebook = mock(AVOCADO.Facebook);
	this.ajax = mock(AVOCADO.Ajax);
	this.viewManager = mock(AVOCADO.ViewManager);

	this.localPlayerId = "3452cba";
	this.gameId = 4;
	this.teams = [[this.localPlayerId, "2b"], ["3c", "4d"]];
	this.scores = [0, 0];
	this.playerNamePromises = {};
	for (var teamId in this.teams) {
		for (var i in this.teams[teamId]) {
			var pid = this.teams[teamId][i];
			this.playerNamePromises[pid] = mock(AVOCADO.PlayerNamePromise);
		}
	}

	this.gameCompleteHtml = "game complete html";
	this.gameCompleteElement = mock(TEST.FakeJQueryElement);

	this.winnerNameElements = [mock(TEST.FakeJQueryElement), mock(TEST.FakeJQueryElement)];

	this.dismissButtonElement = mock(TEST.FakeJQueryElement);
};

GameCompleteDisplayBuilderTest.prototype.doTraining = function(localPlayersTeamWon) {
	when(this.facebook).getSignedInPlayerId().thenReturn(this.localPlayerId);

	when(this.templateRenderer).renderTemplate("gameComplete", allOf(
		hasMember("won", this.locStrings["won"]),
		hasMember("and", this.locStrings["and"]),
		hasMember("dismiss", this.locStrings["dismiss"])
	)).thenReturn(this.gameCompleteHtml);
	when(this.jqueryWrapper).getElement(this.gameCompleteHtml).thenReturn(this.gameCompleteElement);

	for (var pid in this.playerNamePromises) {
		when(this.playerNameDirectory).getNamePromise(pid).thenReturn(this.playerNamePromises[pid]);
	}

	for (var i in this.winnerNameElements) {
		when(this.gameCompleteElement).find(".winner" + i).thenReturn(this.winnerNameElements[i]);
	}

	when(this.gameCompleteElement).find("button.dismiss").thenReturn(this.dismissButtonElement);
};

GameCompleteDisplayBuilderTest.prototype.buildTestObj = function() {
	this.testObj = new AVOCADO.GameCompleteDisplayBuilder(this.templateRenderer, this.jqueryWrapper, this.locStrings, this.playerNameDirectory, this.facebook, this.ajax, this.viewManager);
};

GameCompleteDisplayBuilderTest.prototype.trigger = function() {
	return this.testObj.buildGameCompleteDisplay(this.teams, this.scores, this.gameId);
};

GameCompleteDisplayBuilderTest.prototype.testReturnsExpectedJqueryObject = function() {
	var result = this.trigger();
	assertEquals(this.gameCompleteElement, result);
};

GameCompleteDisplayBuilderTest.prototype.testIncludesYourTeamNamesIfLocalPlayersTeamWon = function() {
	this.scores[0] = 10;
	this.trigger();
	for (i in this.teams[0]) {
		var pid = this.teams[0][i];
		verify(this.playerNamePromises[pid]).registerForUpdates(this.winnerNameElements[i]);
	}
};

GameCompleteDisplayBuilderTest.prototype.testIncludesOtherTeamNamesIfLocalPlayersTeamLost = function() {
	this.scores[1] = 10;
	this.trigger();
	for (i in this.teams[1]) {
		var pid = this.teams[1][i];
		verify(this.playerNamePromises[pid]).registerForUpdates(this.winnerNameElements[i]);
	}
};

GameCompleteDisplayBuilderTest.prototype.testAddsWonClassToElementIfLocalPlayersTeamWon = function() {
	this.scores[0] = 10;
	this.trigger();
	verify(this.gameCompleteElement).addClass("gameWon");
	verify(this.gameCompleteElement, never()).addClass("gameLost");
};

GameCompleteDisplayBuilderTest.prototype.testAddsWonClassToElementIfLocalPlayersTeamLost = function() {
	this.scores[1] = 10;
	this.trigger();
	verify(this.gameCompleteElement).addClass("gameLost");
	verify(this.gameCompleteElement, never()).addClass("gameWon");
};

GameCompleteDisplayBuilderTest.prototype.testAddClickHandlerToDismissButton = function() {
	var clickHandlerFunc = function(event) {};
	this.testObj.buildDismissClickHandler = mockFunction();
	when(this.testObj.buildDismissClickHandler)(this.gameId).thenReturn(clickHandlerFunc);

	this.trigger();

	verify(this.dismissButtonElement).click(clickHandlerFunc);
};

GameCompleteDisplayBuilderTest.prototype.testClickHandlerCallsAjax = function() {
	this.testObj.buildDismissClickHandler(this.gameId)();
	verify(this.ajax).call("dismissCompletedGame", allOf(hasMember("gameId", this.gameId), hasMember("playerId", this.localPlayerId)));
};

GameCompleteDisplayBuilderTest.prototype.testClickHandlerCallsViewManagerAfterAjaxResponseAndDelay = function() {
	var testHarness = this;
	var hasCalledAsync = false;
	setTimeout = function(func, time, lang) {
		verify(testHarness.viewManager, never()).showView("gameList");
		func();
		hasCalledAsync = true;
		verify(testHarness.viewManager).showView("gameList");
	};

	this.ajax = new TEST.FakeAjax();
	this.ajax.callbackResponse = {"success" : true};
	this.buildTestObj();

	this.testObj.buildDismissClickHandler(this.gameId)();
	assertTrue(hasCalledAsync);
};