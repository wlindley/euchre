GameCompleteDisplayBuilderTest = TestCase("GameCompleteDisplayBuilderTest");

GameCompleteDisplayBuilderTest.prototype.setUp = function() {
	this.buildObjects();
	this.doTraining();
	this.buildTestObj();
};

GameCompleteDisplayBuilderTest.prototype.buildObjects = function() {
	this.templateRenderer = mock(AVOCADO.TemplateRenderer);
	this.jqueryWrapper = mock(AVOCADO.JQueryWrapper);
	this.locStrings = {"won" : "won!", "and" : "foo and", "dismiss" : "diss that miss"};
	this.playerNameDirectory = mock(AVOCADO.PlayerNameDirectory);
	this.localPlayerId = "3452cba";

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
};

GameCompleteDisplayBuilderTest.prototype.doTraining = function(localPlayersTeamWon) {
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
};

GameCompleteDisplayBuilderTest.prototype.buildTestObj = function() {
	this.testObj = new AVOCADO.GameCompleteDisplayBuilder(this.templateRenderer, this.jqueryWrapper, this.locStrings, this.playerNameDirectory, this.localPlayerId);
};

GameCompleteDisplayBuilderTest.prototype.trigger = function() {
	return this.testObj.buildGameCompleteDisplay(this.teams, this.scores);
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