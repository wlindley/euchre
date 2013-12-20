RobotsModalBuilderTest = TestCase("RobotsModalBuilderTest");

RobotsModalBuilderTest.prototype.setUp = function() {
	this.teams = [["392349098", "2039482347"], ["23948795"]];
	this.gameId = "saljfwe230sdifsnod";

	this.addRobotsModal = new AVOCADO.AddRobotsModal();
	this.addRobotsModalHtml = "so modal, such html";
	this.addRobotsModalElement = mock(TEST.FakeJQueryElement);
	this.addRobotsModalDropdownElement = mock(TEST.FakeJQueryElement);
	this.modalDeferred = mock(TEST.FakeDeferred);
	this.modalPromise = mock(TEST.FakePromise);
	this.ajaxPromise = mock(TEST.FakePromise);

	this.origModalGetInstance = AVOCADO.AddRobotsModal.getInstance;
	AVOCADO.AddRobotsModal.getInstance = mockFunction();

	this.origSetTimeout = setTimeout;
	setTimeout = function(func, time, lang) {
		func();
	};

	this.templateRenderer = mock(AVOCADO.TemplateRenderer);
	this.jqueryWrapper = mock(AVOCADO.JQueryWrapper);
	this.playerNameDirectory = mock(AVOCADO.PlayerNameDirectory);
	this.dataRetriever = mock(AVOCADO.DataRetriever);
	this.ajax = mock(AVOCADO.Ajax);
	this.viewManager = mock(AVOCADO.ViewManager);

	this.buildObjects();
	this.doTraining();
	this.buildTestObj();
};

RobotsModalBuilderTest.prototype.tearDown = function() {
	AVOCADO.AddRobotsModal.getInstance = this.origModalGetInstance;
	setTimeout = this.origSetTimeout;
};

RobotsModalBuilderTest.prototype.buildObjects = function() {
	this.addRobotsMenuHtmls = [[], []];
	this.existingPlayerNameHtmls = [[], []];
	this.playerNamePromises = {};
	this.playerNameElements = {};
	this.robotTypes = [[], []];
	this.addRobotInputElements = [[], []];
	this.addRobotDropdownElements = [[], []];
	for (var teamId = 0; teamId < 2; teamId++) {
		for (var teamIndex = 0; teamIndex < 2; teamIndex++) {
			var pid = this.teams[teamId][teamIndex];
			this.addRobotsMenuHtmls[teamId][teamIndex] = "menu html for team " + teamId + ", player index " + teamIndex;
			this.existingPlayerNameHtmls[teamId][teamIndex] = "existing player for team " + teamId + ", index " + teamIndex;
			this.playerNamePromises[pid] = mock(AVOCADO.PlayerNamePromise);
			this.playerNameElements[pid] = mock(TEST.FakeJQueryElement);
			this.addRobotInputElements[teamId][teamIndex] = mock(TEST.FakeJQueryElement);
			this.addRobotDropdownElements[teamId][teamIndex] = mock(TEST.FakeJQueryElement);
			if (undefined === pid) {
				this.robotTypes[teamId][teamIndex] = "euchre_robot_easy";
			} else {
				this.robotTypes[teamId][teamIndex] = null;
			}
		}
	}

	this.defaultRobotIndex = 0;
	this.robotData = [
		{
			"id" : "euchre_robot_easy",
			"displayName" : "Easy Robot",
			"default" : true
		},
		{
			"id" : "euchre_robot_hard",
			"displayName" : "Hard Robot"
		}
	];
};

RobotsModalBuilderTest.prototype.doTraining = function() {
	when(AVOCADO.AddRobotsModal.getInstance)(this.addRobotsModalElement).thenReturn(this.addRobotsModal);
	when(this.jqueryWrapper).buildDeferred().thenReturn(this.modalDeferred);
	when(this.modalDeferred).promise().thenReturn(this.modalPromise);
	when(this.ajax).call(anything(), anything()).thenReturn(this.ajaxPromise);

	when(this.addRobotsModalElement).find(".ui.dropdown").thenReturn(this.addRobotsModalDropdownElement);

	var menuListHtml = "";
	for (var i in this.robotData) {
		  var curHtml = "menu html for " + this.robotData[i].id;
		  when(this.templateRenderer).renderTemplate("addRobotsMenuElement", allOf(hasMember("id", this.robotData[i].id), hasMember("displayName", this.robotData[i].displayName))).thenReturn(curHtml);
		  menuListHtml += curHtml;
	}

	var playerNameElementList = mock(TEST.FakeJQueryElement);
	when(this.addRobotsModalElement).find(".playerName").thenReturn(playerNameElementList);
	var addRobotMenuElementList = mock(TEST.FakeJQueryElement);
	when(this.addRobotsModalElement).find(".addRobotsDropdown").thenReturn(addRobotMenuElementList);
	for (var teamId = 0; teamId < 2; teamId++) {
		var teamPlayerNameElementList = mock(TEST.FakeJQueryElement);
		when(playerNameElementList).has("input.team[value=" + teamId + "]").thenReturn(teamPlayerNameElementList);
		var teamAddRobotMenuElementList = mock(TEST.FakeJQueryElement);
		when(addRobotMenuElementList).has("input.team[value=" + teamId + "]").thenReturn(teamAddRobotMenuElementList);
		for (var teamIndex = 0; teamIndex < 2; teamIndex++) {
			when(this.templateRenderer).renderTemplate("addRobotsMenu", allOf(
				hasMember("teamId", teamId),
				hasMember("teamIndex", teamIndex),
				hasMember("defaultId", this.robotData[this.defaultRobotIndex].id),
				hasMember("defaultDisplayName", this.robotData[this.defaultRobotIndex].displayName),
				hasMember("robotList", menuListHtml)
			)).thenReturn(this.addRobotsMenuHtmls[teamId][teamIndex]);
			when(this.templateRenderer).renderTemplate("addRobotsExistingPlayer", allOf(
				hasMember("teamId", teamId),
				hasMember("teamIndex", teamIndex)
			)).thenReturn(this.existingPlayerNameHtmls[teamId][teamIndex]);
			var pid = this.teams[teamId][teamIndex];
			when(this.playerNameDirectory).getNamePromise(pid).thenReturn(this.playerNamePromises[pid]);
			when(teamPlayerNameElementList).has("input.index[value=" + teamIndex + "]").thenReturn(this.playerNameElements[pid]);
			when(teamAddRobotMenuElementList).has("input.index[value=" + teamIndex + "]").thenReturn(this.addRobotDropdownElements[teamId][teamIndex]);
			when(this.addRobotDropdownElements[teamId][teamIndex]).find(".addRobotsInput").thenReturn(this.addRobotInputElements[teamId][teamIndex]);
			when(this.addRobotInputElements[teamId][teamIndex]).val().thenReturn(this.robotTypes[teamId][teamIndex]);
		}
	}

	var player00Element = ((this.teams[0][0] !== undefined) ? this.existingPlayerNameHtmls : this.addRobotsMenuHtmls)[0][0];
	var player01Element = ((this.teams[0][1] !== undefined) ? this.existingPlayerNameHtmls : this.addRobotsMenuHtmls)[0][1];
	var player10Element = ((this.teams[1][0] !== undefined) ? this.existingPlayerNameHtmls : this.addRobotsMenuHtmls)[1][0];
	var player11Element = ((this.teams[1][1] !== undefined) ? this.existingPlayerNameHtmls : this.addRobotsMenuHtmls)[1][1];

	when(this.templateRenderer).renderTemplate("addRobotsModal", allOf(
		hasMember("team0_player0", player00Element),
		hasMember("team0_player1", player01Element),
		hasMember("team1_player0", player10Element),
		hasMember("team1_player1", player11Element)
	)).thenReturn(this.addRobotsModalHtml);
	when(this.jqueryWrapper).getElement(this.addRobotsModalHtml).thenReturn(this.addRobotsModalElement);

	when(this.dataRetriever).get("robots").thenReturn(this.robotData);
};

RobotsModalBuilderTest.prototype.buildTestObj = function() {
	this.testObj = new AVOCADO.AddRobotsModalBuilder(this.templateRenderer, this.jqueryWrapper, this.playerNameDirectory, this.dataRetriever, this.ajax, this.viewManager);
};

RobotsModalBuilderTest.prototype.trigger = function() {
	return this.testObj.buildAddRobotsModal(this.teams, this.gameId);
};

RobotsModalBuilderTest.prototype.testBuildReturnsExpectedValue = function() {
	var result = this.trigger();
	assertEquals(this.addRobotsModal, result);
};

RobotsModalBuilderTest.prototype.testBuildInitializesModalAndDropdowns = function() {
	this.trigger();

	verify(this.addRobotsModalElement).modal("setting", allOf(
		hasMember("duration", 200),
		hasMember("closable", false),
		hasMember("onApprove", this.modalDeferred.resolve),
		hasMember("onDeny", this.modalDeferred.reject)
	));
	verify(this.addRobotsModalDropdownElement).dropdown();
};

RobotsModalBuilderTest.prototype.testBuildHooksUpPlayerNamePromises = function() {
	this.teams[1][1] = "092834923";
	this.buildObjects();
	this.doTraining();

	this.trigger();

	for (var teamId = 0; teamId < 2; teamId++) {
		for (var teamIndex = 0; teamIndex < 2; teamIndex++) {
			var pid = this.teams[teamId][teamIndex];
			verify(this.playerNamePromises[this.teams[teamId][teamIndex]]).registerForUpdates(this.playerNameElements[pid]);
		}
	}
};

RobotsModalBuilderTest.prototype.testConfirmButtonCallsAjax = function() {
	this.modalDeferred = $.Deferred();
	this.modalPromise = this.modalDeferred.promise();
	when(this.jqueryWrapper).buildDeferred().thenReturn(this.modalDeferred);

	this.trigger();
	this.modalDeferred.resolve();

	verify(this.ajax).call("addRobots", allOf(
		hasMember("gameId", this.gameId),
		hasMember("types", this.robotTypes)
	));
};

RobotsModalBuilderTest.prototype.testAjaxResponseShowsGameListViewAfterDelay = function() {
	var testHarness = this;
	var hasCalledAsync = false;
	setTimeout = function(func, time, lang) {
		verify(testHarness.viewManager, never()).showView("gameList");
		func();
		hasCalledAsync = true;
		verify(testHarness.viewManager).showView("gameList");
	};

	this.ajax = new TEST.FakeAjax();
	this.modalDeferred = $.Deferred();
	this.modalPromise = this.modalDeferred.promise();
	when(this.jqueryWrapper).buildDeferred().thenReturn(this.modalDeferred);
	this.buildTestObj();

	this.trigger();
	this.modalDeferred.resolve();
	this.ajax.resolveCall({"success" : true});

	assertTrue(hasCalledAsync);
};

RobotsModalBuilderTest.prototype.testModalGetElementReturnsExpectedElement = function() {
	AVOCADO.AddRobotsModal.getInstance = this.origModalGetInstance;
	var result = this.trigger();
	assertEquals(this.addRobotsModalElement, result.getElement());
};

RobotsModalBuilderTest.prototype.testModalShowDisplaysModal = function() {
	AVOCADO.AddRobotsModal.getInstance = this.origModalGetInstance;
	var result = this.trigger();
	result.show();
	verify(this.addRobotsModalElement).modal("show");
};