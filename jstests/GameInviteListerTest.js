GameInviteListerTest = TestCase("GameInviteListerTest");

GameInviteListerTest.prototype.setUp = function() {
	this.facebook = mock(AVOCADO.Facebook);
	this.ajax = new TEST.FakeAjax();
	this.jqueryWrapper = mock(AVOCADO.JQueryWrapper);

	this.localPlayerId = "12098al3kj4";
	this.deferred = mock(TEST.FakeDeferred);
	this.promise = mock(TEST.FakePromise);
	this.getAppRequestsPromise = $.Deferred();
	this.requests = [
		new AVOCADO.FacebookRequest("03984lsjdf_23ual", "234lka392", "hello, foo"),
		new AVOCADO.FacebookRequest("23049adkfl_23ual", "fdslij234", "hello, foo")
	];
	this.gameDatas = [
		{
			"gameId" : this.requests[0].gameId,
			"status" : "waiting_for_more_players",
			"teams" : [["234lkajd"], []],
			"currentPlayerId" : null
		},
		{
			"gameId" : this.requests[1].gameId,
			"status" : "waiting_for_more_players",
			"teams" : [["234lkajd"], []],
			"currentPlayerId" : null
		}
	];

	this.doTraining();
	this.buildTestObj();
};

GameInviteListerTest.prototype.doTraining = function() {
	when(this.facebook).getSignedInPlayerId().thenReturn(this.localPlayerId);
	when(this.jqueryWrapper).buildDeferred().thenReturn(this.deferred);
	when(this.deferred).promise().thenReturn(this.promise);
	when(this.facebook).getAppRequests().thenReturn(this.getAppRequestsPromise);

};

GameInviteListerTest.prototype.buildTestObj = function() {
	this.testObj = AVOCADO.GameInviteLister.getInstance(this.facebook, this.ajax, this.jqueryWrapper);
};

GameInviteListerTest.prototype.trigger = function() {
	return this.testObj.getGameInviteList();
};

GameInviteListerTest.prototype.testReturnsExpectedPromise = function() {
	var result = this.trigger();
	assertEquals(this.promise, result);
};

GameInviteListerTest.prototype.testCallsAjaxCorrectly = function() {
	this.ajax = mock(AVOCADO.Ajax);
	when(this.ajax).call(anything(), anything()).thenReturn(mock(TEST.FakePromise));
	this.buildTestObj();

	this.trigger();
	this.getAppRequestsPromise.resolve(this.requests);

	verify(this.ajax).call("getBasicGameData", hasMember("gameIds", '["' + this.requests[0].gameId + '", "' + this.requests[1].gameId + '"]'));
};

GameInviteListerTest.prototype.testResolvesPromiseWithExpectedData = function() {
	var resultMatcher = allOf(
		hasMember(0, allOf(
			hasMember("requestId", this.requests[0].requestId),
			hasMember("data", this.gameDatas[0])
		)),
		hasMember(1, allOf(
			hasMember("requestId", this.requests[1].requestId),
			hasMember("data", this.gameDatas[1])
		))
	);

	this.trigger();
	this.getAppRequestsPromise.resolve(this.requests);
	this.ajax.resolveCall({"success" : true, "games" : this.gameDatas});

	verify(this.deferred).resolve(resultMatcher);
};

GameInviteListerTest.prototype.testFiltersOutGamesLocalPlayerIsAlreadyIn = function() {
	this.gameDatas[0].teams[1].push(this.localPlayerId);

	var resultMatcher = allOf(
		hasMember(0, allOf(
			hasMember("requestId", this.requests[1].requestId),
			hasMember("data", this.gameDatas[1])
		))
	);

	this.trigger();
	this.getAppRequestsPromise.resolve(this.requests);
	this.ajax.resolveCall({"success" : true, "games" : this.gameDatas});

	verify(this.deferred).resolve(resultMatcher);
};

GameInviteListerTest.prototype.testDeletesRequestsForGamesPlayerIsAlreadyIn = function() {
	this.gameDatas[0].teams[1].push(this.localPlayerId);

	this.trigger();
	this.getAppRequestsPromise.resolve(this.requests);
	this.ajax.resolveCall({"success" : true, "games" : this.gameDatas});

	verify(this.facebook).deleteAppRequest(this.requests[0].requestId);
};