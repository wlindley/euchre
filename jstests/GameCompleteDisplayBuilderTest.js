GameCompleteDisplayBuilderTest = TestCase("GameCompleteDisplayBuilderTest");

GameCompleteDisplayBuilderTest.prototype.setUp = function() {
	this.buildObjects();
	this.doTraining();
	this.buildTestObj();
};

GameCompleteDisplayBuilderTest.prototype.buildObjects = function() {
	this.templateRenderer = mock(AVOCADO.TemplateRenderer);
	this.jqueryWrapper = mock(AVOCADO.JQueryWrapper);
	this.locStrings = {"yourTeam" : "team 1!", "otherTeam" : "team 2!", "won" : "won!"};
	this.playerNameDirectory = mock(AVOCADO.PlayerNameDirectory);
	this.localPlayerId = "3452cba";

	this.teams = [[this.localPlayerId, "2b"], ["3c", "4d"]];
	this.scores = [0, 0];

	this.gameCompleteHtml = "game complete html";
	this.gameCompleteElement = mock(TEST.FakeJQueryElement);
};

GameCompleteDisplayBuilderTest.prototype.doTraining = function(localPlayersTeamWon) {
	var teamString = this.locStrings["yourTeam"];
	if (this.scores[1] > this.scores[0]) {
		teamString = this.locStrings["otherTeam"];
	}
	when(this.templateRenderer).renderTemplate("gameComplete", allOf(
		hasMember("winningTeam", teamString),
		hasMember("won", this.locStrings["won"])
	)).thenReturn(this.gameCompleteHtml);
	when(this.jqueryWrapper).getElement(this.gameCompleteHtml).thenReturn(this.gameCompleteElement);
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

GameCompleteDisplayBuilderTest.prototype.testIncludesYourTeamIfLocalPlayersTeamWon = function() {
	this.scores[0] = 10;
	var result = this.trigger();
	assertEquals(this.gameCompleteElement, result);
};

GameCompleteDisplayBuilderTest.prototype.testIncludesOtherTeamIfLocalPlayersTeamLost = function() {
	this.buildObjects();
	this.scores[1] = 10;
	this.doTraining();
	this.buildTestObj();
	var result = this.trigger();
	assertEquals(this.gameCompleteElement, result);
};