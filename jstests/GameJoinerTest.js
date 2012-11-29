GameJoinerTest = TestCase("GameJoinerTest");

GameJoinerTest.prototype.setUp = function() {
	this.fbId = "1234567";
	this.ajax = mock(AVOCADO.Ajax);
	this.txtGameId = mock(TEST.FakeJQueryElement);
	this.txtTeamId = mock(TEST.FakeJQueryElement);
	this.btnJoinGame = mock(TEST.FakeJQueryElement);
	this.buildTestObj();
};

GameJoinerTest.prototype.testJoinGameFromTextFieldsCallsAjaxWithCorrectData = function() {
	var gameId = "1384";
	var teamId = "1";
	when(this.txtGameId).val().thenReturn(gameId);
	when(this.txtTeamId).val().thenReturn(teamId);

	this.testObj.joinGameFromTextFields();

	verify(this.ajax).call("addPlayer", allOf(hasMember("gameId", gameId), hasMember("team", teamId), hasMember("playerId", this.fbId)), func());
};

GameJoinerTest.prototype.testInitBindsJoinGameButton = function() {
	this.testObj.init();

	verify(this.btnJoinGame).click(this.testObj.joinGameFromTextFields);
};

GameJoinerTest.prototype.buildTestObj = function() {
	this.testObj = new AVOCADO.GameJoiner(this.fbId, this.ajax, this.txtGameId, this.txtTeamId, this.btnJoinGame);
};
