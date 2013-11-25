FacebookTest = TestCase("FacebookTest");

FakeFB = function() {
	this.init = function() {};
	this.login = function() {};
	this.api = function() {};
};

FacebookTest.prototype.setUp = function() {
	window.FB = null;
	this.jqueryWrapper = mock(AVOCADO.JQueryWrapper);
	this.appId = "234023984";
	this.localPlayerId = "324lkjada34l";
	this.channelUrl = "http://my.awesome.com/channel.html";
	this.otherPlayerId = "slajf323409imsde3";
	this.otherPlayerName = "Foobing Barbazi";

	this.initDeferred = mock(TEST.FakeDeferred);
	this.initPromise = mock(TEST.FakePromise);

	this.successCallback = mockFunction();
	this.failureCallback = mockFunction();
	this.getPlayerDataCallback = mockFunction();

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
	when(this.jqueryWrapper).buildDeferred().thenReturn(this.initDeferred);
};

FacebookTest.prototype.trigger = function() {
	return this.testObj.init({
		"success" : this.successCallback,
		"failure" : this.failureCallback
	});
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
		testHarness.testObj.buildGetPlayerDataCallback(testHarness.getPlayerDataCallback)({"name" : testHarness.otherPlayerName, "id" : testHarness.otherPlayerId});
	});
};

FacebookTest.prototype.setupGetNameCallError = function() {
	var testHarness = this;
	when(FB).api("/" + this.otherPlayerId + "?fields=name,id", func()).then(function() {
		testHarness.testObj.buildGetPlayerDataCallback(testHarness.getPlayerDataCallback)({"error" : {"message" : "foo"}});
	});
};

FacebookTest.prototype.testInitLoadsFBScript = function() {
	this.trigger();
	verify(this.jqueryWrapper).ajax("//connect.facebook.net/en_US/all.js", allOf(
		hasMember("dataType", "script"),
		hasMember("success", this.testObj.handleAjaxResponse),
		hasMember("cache", true)
	));
};

FacebookTest.prototype.testHandleAjaxResponseInitializesFB = function() {
	this.setupAjaxCall();

	this.trigger();
	verify(window.FB).init(allOf(
		hasMember("appId", this.appId),
		hasMember("channelUrl", this.channelUrl),
		hasMember("status", true),
		hasMember("cookie", true)
	));
};

FacebookTest.prototype.testHandleAjaxResponseLogsIn = function() {
	this.setupAjaxCall();

	this.trigger();

	verify(window.FB).login(func());
};

FacebookTest.prototype.testHandleAjaxResponseInitsBeforeLoggingIn = function() {
	window.FB = mock(FakeFB);
	this.jqueryWrapper.ajax = function(url, params) {
		params["success"]();
	};
	when(window.FB).init().thenThrow("Exception!");

	try {
		this.trigger();
	} catch (e) {
		//ignore
	}

	verify(window.FB).init();
	verify(window.FB, never()).login(anything());
};

FacebookTest.prototype.testInitReturnsExpectedPromise = function() {
	var result = this.trigger();
	assertEquals(this.initPromise, result);
};

FacebookTest.prototype.testMultipleInitsReturnsSamePromiseAndDoesNotReinitialize = function() {
	when(this.jqueryWrapper).buildDeferred().thenReturn(this.initDeferred).thenReturn(null);
	var firstResult = this.trigger();
	var secondResult = this.trigger();
	verify(this.jqueryWrapper, once()).ajax(anything(), anything());
	assertEquals(this.initPromise, firstResult);
	assertEquals(this.initPromise, secondResult);
};

FacebookTest.prototype.testPromiseResolvedOnSuccessfulLogin = function() {
	this.setupAjaxCall(true);
	this.trigger();
	verify(this.initDeferred).resolve();
};

FacebookTest.prototype.testPromiseRejectedOnFailedLogin = function() {
	this.setupAjaxCall(false);
	this.trigger();
	verify(this.initDeferred).reject();
};

FacebookTest.prototype.testGetSignedInPlayerIdReturnsExpectedDataAfterLoggingIn = function() {
	this.setupAjaxCall(true);

	this.trigger();

	assertEquals(this.localPlayerId, this.testObj.getSignedInPlayerId());
};

FacebookTest.prototype.testGetSignedInPlayerIdReturnsEmptyStringAfterLoginFailure = function() {
	this.setupAjaxCall(false);

	this.trigger();

	assertEquals("", this.testObj.getSignedInPlayerId());
};

FacebookTest.prototype.testGetSignedInPlayerIdReturnsEmptyStringIfHaveNotLoggedIn = function() {
	this.trigger();
	assertEquals("", this.testObj.getSignedInPlayerId());
};

FacebookTest.prototype.testGetPlayerDataCallsCallbackWithName = function() {
	this.setupAjaxCall();
	this.trigger();
	this.setupGetNameCallSuccess();

	this.testObj.getPlayerData(this.otherPlayerId, this.getPlayerDataCallback);
	verify(this.getPlayerDataCallback)(allOf(
		hasMember("name", this.otherPlayerName),
		hasMember("playerId", this.otherPlayerId)
	));
};

FacebookTest.prototype.testGetPlayerNameCallsCallbackWithEmptyObject = function() {
	this.setupAjaxCall();
	this.trigger();
	this.setupGetNameCallError();

	this.testObj.getPlayerData(this.otherPlayerId, this.getPlayerDataCallback);
	verify(this.getPlayerDataCallback)(anything());
};