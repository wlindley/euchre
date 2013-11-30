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

	this.requestTitle = "bestest request title";
	this.requestMessage = "send this awesome request";
	this.data = {"key" : "value"};

	this.initDeferred = mock(TEST.FakeDeferred);
	this.initPromise = mock(TEST.FakePromise);
	this.getPlayerDataDeferred = mock(TEST.FakeDeferred);
	this.getPlayerDataPromise = mock(TEST.FakePromise);
	this.sendRequestsDeferred = mock(TEST.FakeDeferred);
	this.sendRequestsPromise = mock(TEST.FakePromise);

	this.sendRequestCallback = mockFunction();

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
	when(this.jqueryWrapper).buildDeferred().thenReturn(this.initDeferred).thenReturn(this.getPlayerDataDeferred);
};

FacebookTest.prototype.triggerInit = function() {
	return this.testObj.init();
};

FacebookTest.prototype.setupAjaxCall = function(trainingValueForLogin) {
	var testHarness = this;
	this.jqueryWrapper.ajax = function(url, params) {
		window.FB = mock(FakeFB);
		if (undefined !== trainingValueForLogin) {
			window.FB.login = function(func) {
				var response = trainingValueForLogin;
				if (trainingValueForLogin) {
					response = {"authResponse" : {"userID" : testHarness.localPlayerId}}; //this structure mimics Facebook's response as of 20131119
				}
				func(response);
			};
		}
		params["success"]();
	};
};

FacebookTest.prototype.setupGetNameCallSuccess = function() {
	var testHarness = this;
	when(FB).api("/" + this.otherPlayerId + "?fields=name,id", func()).then(function() {
		testHarness.testObj.getPlayerDataCallback({"name" : testHarness.otherPlayerName, "id" : testHarness.otherPlayerId});
	});
};

FacebookTest.prototype.setupGetNameCallError = function() {
	var testHarness = this;
	when(FB).api("/" + this.otherPlayerId + "?fields=name,id", func()).then(function() {
		testHarness.testObj.getPlayerDataCallback({"error" : {"message" : "foo"}});
	});
};

FacebookTest.prototype.setupSendRequests = function() {
	when(this.jqueryWrapper).buildDeferred().thenReturn(this.initDeferred).thenReturn(this.sendRequestsDeferred);
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

FacebookTest.prototype.testHandleAjaxResponseLogsIn = function() {
	this.setupAjaxCall();

	this.triggerInit();

	verify(window.FB).login(func());
};

FacebookTest.prototype.testHandleAjaxResponseInitsBeforeLoggingIn = function() {
	window.FB = mock(FakeFB);
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
	verify(window.FB, never()).login(anything());
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
	this.setupAjaxCall(true);
	this.triggerInit();
	verify(this.initDeferred).resolve();
};

FacebookTest.prototype.testPromiseRejectedOnFailedLogin = function() {
	this.setupAjaxCall(false);
	this.triggerInit();
	verify(this.initDeferred).reject();
};

FacebookTest.prototype.testGetSignedInPlayerIdReturnsExpectedDataAfterLoggingIn = function() {
	this.setupAjaxCall(true);

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

	this.testObj.getPlayerData(this.otherPlayerId);

	verify(this.getPlayerDataDeferred).resolve();
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

FacebookTest.prototype.triggerSendRequests = function() {
	return this.testObj.sendRequests(this.requestTitle, this.requestMessage, this.requestData);
}

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