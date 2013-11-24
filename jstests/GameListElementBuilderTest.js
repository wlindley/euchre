GameListElementBuilderTest = TestCase("GameListElementBuilderTest");

GameListElementBuilderTest.prototype.setUp = function() {
	this.jqueryWrapper = mock(AVOCADO.JQueryWrapper);
	this.templateRenderer = mock(AVOCADO.TemplateRenderer);
	this.locStrings = {
		"vs" : "some versus",
		"n/a" : "N/A",
		"inviteCTA" : "invite",
		"round_in_progress" : "foo",
		"waiting_for_more_players" : "bar",
		"trump_selection" : "baz"
	};
	this.playerNameDirectory = mock(AVOCADO.PlayerNameDirectory);
	this.facebook = mock(AVOCADO.Facebook);

	this.elementHtml = "html for list element";
	this.element = mock(TEST.FakeJQueryElement);
	this.gameId = "asdlkj324";
	this.playerId = "1209daslkj";
	this.otherPlayerId = "23klsadf39";
	this.team = [[this.otherPlayerId, "3456"], [this.playerId, "1234"]];
	this.currentPlayerId = this.playerId;

	this.element = mock(TEST.FakeJQueryElement);
	this.linkElement = mock(TEST.FakeJQueryElement);
	this.turnNameElement = mock(TEST.FakeJQueryElement);
	this.turnElement = mock(TEST.FakeJQueryElement);
	this.namePromises = {};
	this.tableElement = mock(TEST.FakeJQueryElement);
	this.tableDataElements = [];
	this.tableDataNameElements = [];

	this.showGameDataFunc = mockFunction();

	this.buildTestObj();
};

GameListElementBuilderTest.prototype.buildTestObj = function() {
	this.testObj = new AVOCADO.GameListElementBuilder(this.jqueryWrapper, this.templateRenderer, this.locStrings, this.playerNameDirectory, this.facebook);
};

GameListElementBuilderTest.prototype.doTraining = function(status) {
	this.status = status
	this.gameData = {
		"gameId" : this.gameId,
		"status" : this.status,
		"currentPlayerId" : this.currentPlayerId,
		"teams" : this.team
	};

	when(this.templateRenderer).renderTemplate("gameListEntry", allOf(
		hasMember("vs", this.locStrings["vs"]),
		hasMember("gameId", this.gameId),
		hasMember("status", this.locStrings[status])
	)).thenReturn(this.elementHtml);
	when(this.jqueryWrapper).getElement(this.elementHtml).thenReturn(this.element);

	when(this.facebook).getSignedInPlayerId().thenReturn(this.playerId);

	for (var j = 0; j < 2; j++) {
		var teamTableElements = [];
		var teamNameElements = [];
		for (var k = 0; k < 2; k++) {
			if ((j in this.team) && (k in this.team[j])) {
				var pid = this.team[j][k];
				this.namePromises[pid] = mock(AVOCADO.PlayerNamePromise);
			}
			teamTableElements.push(mock(TEST.FakeJQueryElement));
			teamNameElements.push(mock(TEST.FakeJQueryElement));
		}
		this.tableDataElements.push(teamTableElements);
		this.tableDataNameElements.push(teamNameElements);
	}

	for (var pid in this.namePromises) {
		when(this.playerNameDirectory).getNamePromise(pid).thenReturn(this.namePromises[pid]);
	}

	when(this.element).find(".viewGameData").thenReturn(this.linkElement);
	when(this.element).find(".gameListElementTeams").thenReturn(this.tableElement);
	when(this.element).find(".turn").thenReturn(this.turnElement);
	when(this.turnElement).find(".playerName").thenReturn(this.turnNameElement);
	var tableDataSelector = mock(TEST.FakeJQueryElement);
	when(this.tableElement).find("td").thenReturn(tableDataSelector);
	for (var j in this.tableDataElements) {
		var teamSelector = mock(TEST.FakeJQueryElement);
		when(tableDataSelector).has("input.team[value=" + j + "]").thenReturn(teamSelector);
		for (var k in this.tableDataElements[j]) {
			when(teamSelector).has("input.index[value=" + k + "]").thenReturn(this.tableDataElements[j][k]);
			when(this.tableDataElements[j][k]).find(".playerName").thenReturn(this.tableDataNameElements[j][k]);
		}
	}
};

GameListElementBuilderTest.prototype.trigger = function() {
	return this.testObj.buildListElement(this.gameData, this.showGameDataFunc);
};

GameListElementBuilderTest.prototype.testBuildListElementReturnsExpectedObject = function() {
	this.doTraining("round_in_progress");
	assertEquals(this.element, this.trigger());
};

GameListElementBuilderTest.prototype.testHooksUpTurnNamePromise = function() {
	this.doTraining("trump_selection");
	this.trigger();
	verify(this.namePromises[this.currentPlayerId]).registerForUpdates(this.turnNameElement);
};

GameListElementBuilderTest.prototype.testSetsExpectedStringForNullCurrentPlayer = function() {
	this.currentPlayerId = null;
	this.doTraining("round_in_progress");
	this.trigger();
	verify(this.turnNameElement).text(this.locStrings["n/a"]);
};

GameListElementBuilderTest.prototype.testHooksUpTeamNamePromisesAndCTAs = function() {
	this.team = [this.team[0], [this.team[1][0]]];
	this.doTraining("waiting_for_more_players");
	this.trigger();
	for (var j = 0; j < 2; j++) {
		for (var k = 0; k < 2; k++) {
			if ((j in this.team) && (k in this.team[j])) {
				var pid = this.team[j][k];
				verify(this.namePromises[pid]).registerForUpdates(this.tableDataNameElements[j][k]);
			} else {
				verify(this.tableDataNameElements[j][k]).text(this.locStrings["inviteCTA"]);
			}
		}
	}
};

GameListElementBuilderTest.prototype.testHooksUpClickHandler = function() {
	this.doTraining("round_in_progress");
	this.trigger();
	verify(this.linkElement).click(this.showGameDataFunc);
};

GameListElementBuilderTest.prototype.testDoesNotHookUpClickHandlerIfGameNotStarted = function() {
	this.currentPlayerId = null;
	this.doTraining("waiting_for_more_players");
	this.trigger();
	verify(this.linkElement, never()).click(this.showGameDataFunc);
};

GameListElementBuilderTest.prototype.testNeverRemovesClassesIfCurrentPlayersTurn = function() {
	this.doTraining("round_in_progress");
	this.trigger();
	verify(this.element, never()).removeClass("gameListEntryClickable");
	verify(this.element, never()).removeClass("gameListEntryYourTurn");
};

GameListElementBuilderTest.prototype.testRemovesClassesIfStatusIsWaitingForMorePlayers = function() {
	this.currentPlayerId = null;
	this.doTraining("waiting_for_more_players");
	this.trigger();
	verify(this.element).removeClass("gameListEntryClickable");
	verify(this.element).removeClass("gameListEntryYourTurn");
};

GameListElementBuilderTest.prototype.testRemovesClassNotLocalPlayersTurn = function() {
	this.currentPlayerId = this.otherPlayerId;
	this.doTraining("round_in_progress");
	this.trigger();
	verify(this.element, never()).removeClass("gameListEntryClickable");
	verify(this.element).removeClass("gameListEntryYourTurn");
};