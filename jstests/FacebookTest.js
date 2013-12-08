FacebookTest = TestCase("FacebookTest");

FakeFB = function() {
	this.init = function() {};
	this.login = function() {};
	this.api = function() {};
	this.ui = function() {};
};

FacebookTest.prototype.setUp = function() {
	window.FB = null;
	this.jqueryWrapper = mock(AVOCADO.JQueryWrapper);
	this.appId = "234023984";
	this.localPlayerId = "324lkjada34l";
	this.channelUrl = "http://my.awesome.com/channel.html";
	this.otherPlayerId = "slajf323409imsde3";
	this.otherPlayerName = "Foobing Barbazi";
	this.otherPlayerFirstName = "Foobing";
	this.otherPlayerLastName = "Barbazi";

	this.requestTitle = "bestest request title";
	this.requestMessage = "send this awesome request";
	this.data = {"key" : "value"};

	this.rawRequests = [
		{
			"data" : '{"gameId" : "23lkjasl3k"}',
			"id" : "lkaslk3_239isdfalk",
			"message" : "hello, euchre"
		},
		{
			"data" : '{"gameId" : "fsal3230sdfa"}',
			"id" : "sdjhsk3j3s_239isdfalk",
			"message" : "hello, euchre"
		}
	];
	this.requestsVerifier = allOf(
		hasMember(0, allOf(
			hasMember("gameId", "23lkjasl3k"),
			hasMember("requestId", "lkaslk3_239isdfalk"),
			hasMember("message", "hello, euchre")
		)),
		hasMember(1, allOf(
			hasMember("gameId", "fsal3230sdfa"),
			hasMember("requestId", "sdjhsk3j3s_239isdfalk"),
			hasMember("message", "hello, euchre")
		))
	);
	when(this.jqueryWrapper).jsonDecode('{"gameId" : "23lkjasl3k"}').thenReturn({"gameId" : "23lkjasl3k"});
	when(this.jqueryWrapper).jsonDecode('{"gameId" : "fsal3230sdfa"}').thenReturn({"gameId" : "fsal3230sdfa"});

	this.deleteRequestId = "320948adlkjf_203948adj";

	this.loginCalled = false;

	this.initDeferred = mock(TEST.FakeDeferred);
	this.initPromise = mock(TEST.FakePromise);
	this.getPlayerDataDeferred = mock(TEST.FakeDeferred);
	this.getPlayerDataPromise = mock(TEST.FakePromise);
	this.sendRequestsDeferred = mock(TEST.FakeDeferred);
	this.sendRequestsPromise = mock(TEST.FakePromise);
	this.getAppRequestsDeferred = mock(TEST.FakeDeferred);
	this.getAppRequestsPromise = mock(TEST.FakePromise);
	this.deleteAppRequestDeferred = mock(TEST.FakeDeferred);
	this.deleteAppRequestPromise = mock(TEST.FakePromise);

	this.sendRequestCallback = mockFunction();
	this.getAppRequestsCallback = mockFunction();

	this.doTraining();
	this.buildTestObj();
};

FacebookTest.prototype.tearDown = function() {
	window.FB = undefined;
};

FacebookTest.prototype.buildTestObj = function() {
	this.testObj = AVOCADO.Facebook.getInstance(this.jqueryWrapper, this.appId, this.channelUrl);	
};

FacebookTest.prototype.doTraining = function() {
	when(this.initDeferred).promise().thenReturn(this.initPromise);
	when(this.getPlayerDataDeferred).promise().thenReturn(this.getPlayerDataPromise);
	when(this.sendRequestsDeferred).promise().thenReturn(this.sendRequestsPromise);
	when(this.getAppRequestsDeferred).promise().thenReturn(this.getAppRequestsPromise);
	when(this.deleteAppRequestDeferred).promise().thenReturn(this.deleteAppRequestPromise);
	when(this.jqueryWrapper).buildDeferred().thenReturn(this.initDeferred).thenReturn(this.getPlayerDataDeferred);
};

FacebookTest.prototype.triggerInit = function() {
	return this.testObj.init();
};

FacebookTest.prototype.triggerSendRequests = function() {
	return this.testObj.sendRequests(this.requestTitle, this.requestMessage, this.requestData);
};

FacebookTest.prototype.triggerGetAppRequests = function() {
	return this.testObj.getAppRequests();
};

FacebookTest.prototype.triggerDeleteAppRequest = function() {
	return this.testObj.deleteAppRequest(this.deleteRequestId);
};

FacebookTest.prototype.setupAjaxCall = function(trainingValueForLogin, authStatus, updatedAuthStatus) {
	var testHarness = this;
	this.jqueryWrapper.ajax = function(url, params) {
		window.FB = mock(FakeFB);
		window.FB.Event = {}
		window.FB.Event.subscribe = mockFunction();
		if (undefined !== trainingValueForLogin) {
			var response = trainingValueForLogin;
			if (trainingValueForLogin) {
				//this structure mimics Facebook's response as of 20131208
				var status = "connected";
				if (authStatus) {
					status = authStatus;
				}
				response = {
					"status" : status,
					"authResponse" : {
						"userID" : testHarness.localPlayerId
					}
				};
			}
			var callback = mockFunction();

			window.FB.login = function() {
				if (updatedAuthStatus) {
					response.status = updatedAuthStatus;
				} else {
					response.status = "connected";
				}
				testHarness.loginCalled = true;
				callback(response);
			};
			window.FB.Event.subscribe = function(eventName, func) {
				callback = func;
				callback(response);
			};
		}
		params["success"]();
	};
};

FacebookTest.prototype.setupGetNameCallSuccess = function() {
	var testHarness = this;
	when(FB).api("/" + this.otherPlayerId + "?fields=name,id,first_name,last_name", func()).then(function() {
		testHarness.testObj.getPlayerDataCallback({"name" : testHarness.otherPlayerName, "id" : testHarness.otherPlayerId, "first_name" : testHarness.otherPlayerFirstName, "last_name" : testHarness.otherPlayerLastName});
	});
};

FacebookTest.prototype.setupGetNameCallError = function() {
	var testHarness = this;
	when(FB).api("/" + this.otherPlayerId + "?fields=name,id,first_name,last_name", func()).then(function() {
		testHarness.testObj.getPlayerDataCallback({"error" : {"message" : "foo"}});
	});
};

FacebookTest.prototype.setupSendRequests = function() {
	when(this.jqueryWrapper).buildDeferred().thenReturn(this.initDeferred).thenReturn(this.sendRequestsDeferred);
};

FacebookTest.prototype.setupGetAppRequests = function() {
	when(this.jqueryWrapper).buildDeferred().thenReturn(this.initDeferred).thenReturn(this.getAppRequestsDeferred);
};

FacebookTest.prototype.setupDeleteAppRequest = function() {
	when(this.jqueryWrapper).buildDeferred().thenReturn(this.initDeferred).thenReturn(this.deleteAppRequestDeferred);
};

FacebookTest.prototype.testInitLoadsFBScript = function() {
	this.triggerInit();
	verify(this.jqueryWrapper).ajax("//connect.facebook.net/en_US/all.js", allOf(
		hasMember("dataType", "script"),
		hasMember("success", this.testObj.handleAjaxResponse),
		hasMember("cache", true)
	));
};

FacebookTest.prototype.testHandleAjaxResponseInitializesFB = function() {
	this.setupAjaxCall();

	this.triggerInit();
	verify(window.FB).init(allOf(
		hasMember("appId", this.appId),
		hasMember("channelUrl", this.channelUrl),
		hasMember("status", true),
		hasMember("cookie", true),
		hasMember("frictionlessRequests", true)
	));
};

FacebookTest.prototype.testHandleAjaxResponse = function() {
	this.setupAjaxCall();

	this.triggerInit();

	verify(window.FB.Event.subscribe)("auth.authResponseChange", func());
};

FacebookTest.prototype.testHandleAjaxResponseInitsBeforeLoggingIn = function() {
	window.FB = mock(FakeFB);
	window.FB.Event = {};
	window.FB.Event.subscribe = mockFunction();
	this.jqueryWrapper.ajax = function(url, params) {
		params["success"]();
	};
	when(window.FB).init().thenThrow("Exception!");

	try {
		this.triggerInit();
	} catch (e) {
		//ignore
	}

	verify(window.FB).init();
	verify(window.FB.Event.subscribe, never())(anything());
};

FacebookTest.prototype.testInitReturnsExpectedPromise = function() {
	var result = this.triggerInit();
	assertEquals(this.initPromise, result);
};

FacebookTest.prototype.testMultipleInitsReturnsSamePromiseAndDoesNotReinitialize = function() {
	when(this.jqueryWrapper).buildDeferred().thenReturn(this.initDeferred).thenReturn(null);
	var firstResult = this.triggerInit();
	var secondResult = this.triggerInit();
	verify(this.jqueryWrapper, once()).ajax(anything(), anything());
	assertEquals(this.initPromise, firstResult);
	assertEquals(this.initPromise, secondResult);
};

FacebookTest.prototype.testPromiseResolvedOnSuccessfulLogin = function() {
	this.setupAjaxCall(true, "connected");
	this.triggerInit();
	verify(this.initDeferred).resolve();
};

FacebookTest.prototype.testLoginsInIfNotLoggedIn = function() {
	this.setupAjaxCall(true, "not_authorized", "connected");
	this.triggerInit();
	assertTrue(this.loginCalled); //cannot verify since we've replaced the mock function
};

FacebookTest.prototype.testMultipleLoginFailuresRejectsPromise = function() {
	this.setupAjaxCall(true, "unknown", "not_authorized");
	this.triggerInit();
	verify(this.initDeferred).reject();
};

FacebookTest.prototype.testGetSignedInPlayerIdReturnsExpectedDataAfterLoggingIn = function() {
	this.setupAjaxCall(true, "connected");

	this.triggerInit();

	assertEquals(this.localPlayerId, this.testObj.getSignedInPlayerId());
};

FacebookTest.prototype.testGetSignedInPlayerIdReturnsEmptyStringAfterLoginFailure = function() {
	this.setupAjaxCall(false);

	this.triggerInit();

	assertEquals("", this.testObj.getSignedInPlayerId());
};

FacebookTest.prototype.testGetSignedInPlayerIdReturnsEmptyStringIfHaveNotLoggedIn = function() {
	this.triggerInit();
	assertEquals("", this.testObj.getSignedInPlayerId());
};

FacebookTest.prototype.testGetPlayerDataReturnsPromise = function() {
	this.setupAjaxCall();
	this.triggerInit();
	var result = this.testObj.getPlayerData(this.otherPlayerId);
	assertEquals(this.getPlayerDataPromise, result);
};

FacebookTest.prototype.testGetPlayerDataResolvesPromiseOnSuccess = function() {
	this.setupAjaxCall();
	this.triggerInit();
	this.setupGetNameCallSuccess();

	var expectedName = this.otherPlayerFirstName + " " + this.otherPlayerLastName[0] + ".";

	this.testObj.getPlayerData(this.otherPlayerId);

	verify(this.getPlayerDataDeferred).resolve(allOf(
		hasMember("playerId", this.otherPlayerId),
		hasMember("name", expectedName)
	));
};

FacebookTest.prototype.testGetPlayerDataDoesNotResolvePromiseOnFailure = function() {
	this.setupAjaxCall();
	this.triggerInit();
	this.setupGetNameCallError();

	this.testObj.getPlayerData(this.otherPlayerId);

	verify(this.getPlayerDataDeferred, never()).resolve();
};

FacebookTest.prototype.testRepeatedGetPlayerDataReturnsSamePromiseAndOnlyCallsFacebookOnce = function() {
	when(this.jqueryWrapper).buildDeferred().thenReturn(this.initDeferred).thenReturn(this.getPlayerDataDeferred).thenReturn(null);
	this.setupAjaxCall();
	this.triggerInit();
	this.setupGetNameCallSuccess();

	var firstResult = this.testObj.getPlayerData(this.otherPlayerId);
	var secondResult = this.testObj.getPlayerData(this.otherPlayerId);

	verify(FB, once()).api(anything(), anything());
	assertEquals(this.getPlayerDataPromise, firstResult);
	assertEquals(this.getPlayerDataPromise, secondResult);
};

FacebookTest.prototype.testSendRequestsReturnsExpectedPromise = function() {
	this.setupAjaxCall();
	this.setupSendRequests();
	this.triggerInit();

	var result = this.triggerSendRequests();

	assertEquals(this.sendRequestsPromise, result);
};

FacebookTest.prototype.testSendRequestsCallsFBUI = function() {
	this.setupAjaxCall();
	this.setupSendRequests();
	this.testObj.buildSendRequestsCallback = mockFunction();
	when(this.testObj.buildSendRequestsCallback)(this.sendRequestsDeferred).thenReturn(this.sendRequestCallback);

	this.triggerInit();
	this.triggerSendRequests();

	verify(FB).ui(allOf(
		hasMember("method", "apprequests"),
		hasMember("app_id", this.appId),
		hasMember("title", this.requestTitle),
		hasMember("message", this.requestMessage),
		hasMember("data", this.requestData)
	), this.sendRequestCallback);
};

FacebookTest.prototype.testSendRequestsCallbackResolvesDeferred = function() {
	this.setupAjaxCall();
	this.setupSendRequests();

	var requestId = "203942034alfj";
	var toList = ["3lm3l2"];

	this.triggerInit();
	this.testObj.buildSendRequestsCallback(this.sendRequestsDeferred)(requestId, toList);

	verify(this.sendRequestsDeferred).resolve(toList);
};

FacebookTest.prototype.testSendRequestsCallbackRejectsDeferredIfUserCancels = function() {
	this.setupAjaxCall();
	this.setupSendRequests();

	var requestId = null;
	var toList = undefined;

	this.triggerInit();
	this.testObj.buildSendRequestsCallback(this.sendRequestsDeferred)(requestId, toList);

	verify(this.sendRequestsDeferred).reject();
};

FacebookTest.prototype.testGetAppRequestsReturnsExpectedPromise = function() {
	this.setupAjaxCall();
	this.setupGetAppRequests();

	this.triggerInit();
	var result = this.triggerGetAppRequests();

	assertEquals(this.getAppRequestsPromise, result);
};

FacebookTest.prototype.testGetAppRequestsCallsFBAPI = function() {
	this.setupAjaxCall(true);
	this.setupGetAppRequests();
	this.testObj.buildGetAppRequestsCallback = mockFunction();
	when(this.testObj.buildGetAppRequestsCallback)(this.getAppRequestsDeferred).thenReturn(this.getAppRequestsCallback);

	this.triggerInit();
	this.triggerGetAppRequests();

	verify(FB).api("/" + this.localPlayerId + "/apprequests", this.getAppRequestsCallback);
};

FacebookTest.prototype.testGetAppRequestsCallbackResolvesDeferred = function() {
	this.setupAjaxCall(true);
	this.setupGetAppRequests();

	this.triggerInit();
	this.testObj.buildGetAppRequestsCallback(this.getAppRequestsDeferred)({"data" : this.rawRequests});

	verify(this.getAppRequestsDeferred).resolve(this.requestsVerifier);
};

FacebookTest.prototype.testDeleteAppRequestReturnsExpectedPromise = function() {
	this.setupAjaxCall();
	this.setupDeleteAppRequest();

	this.triggerInit();
	var result = this.triggerDeleteAppRequest();

	assertEquals(this.deleteAppRequestPromise, result);
};

FacebookTest.prototype.testDeleteAppRequestCallsFBAPI = function() {
	var deleteAppRequestCallback = mockFunction();
	this.setupAjaxCall(true);
	this.setupDeleteAppRequest();
	this.testObj.buildDeleteAppRequestCallback = mockFunction();
	when(this.testObj.buildDeleteAppRequestCallback)(this.deleteAppRequestDeferred).thenReturn(deleteAppRequestCallback);

	this.triggerInit();
	this.triggerDeleteAppRequest();

	verify(FB).api("/" + this.deleteRequestId, "delete", deleteAppRequestCallback);
};

FacebookTest.prototype.testDeleteAppRequestCallbackResolvesDeferredWhenFBCallSucceeds = function() {
	this.setupAjaxCall(true);
	this.setupDeleteAppRequest();

	this.triggerInit();
	this.testObj.buildDeleteAppRequestCallback(this.deleteAppRequestDeferred)(true);

	verify(this.deleteAppRequestDeferred).resolve();
};

FacebookTest.prototype.testDeleteAppRequestCallbackRejectsDeferredWhenFBCallFails = function() {
	this.setupAjaxCall(true);
	this.setupDeleteAppRequest();

	this.triggerInit();
	this.testObj.buildDeleteAppRequestCallback(this.deleteAppRequestDeferred)({"error" : {"message" : "foo", "code" : 803}});

	verify(this.deleteAppRequestDeferred).reject();
};