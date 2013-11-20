FacebookTest = TestCase("FacebookTest");

FakeFB = function() {
	this.init = function() {};
	this.login = function() {};
};

FacebookTest.prototype.setUp = function() {
	window.FB = null;
	this.jqueryWrapper = mock(AVOCADO.JQueryWrapper);
	this.appId = "234023984";
	this.localPlayerId = "324lkjada34l";
	this.channelUrl = "http://my.awesome.com/channel.html";

	this.successCallback = mockFunction();
	this.failureCallback = mockFunction();

	this.buildTestObj();
};

FacebookTest.prototype.tearDown = function() {
	window.FB = undefined;
};

FacebookTest.prototype.buildTestObj = function() {
	this.testObj = AVOCADO.Facebook.getInstance(this.jqueryWrapper, this.appId, this.channelUrl);	
};

FacebookTest.prototype.trigger = function() {
	var testHarness = this;
	this.testObj.init({
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

FacebookTest.prototype.testLoginSuccessCallbackIsCalled = function() {
	this.setupAjaxCall(true);

	this.trigger();

	verify(this.successCallback)();
	verifyZeroInteractions(this.failureCallback);
};

FacebookTest.prototype.testLoginFailureCallbackIsCalled = function() {
	this.setupAjaxCall(false);

	this.trigger();

	verifyZeroInteractions(this.successCallback);
	verify(this.failureCallback)();
};

FacebookTest.prototype.testHandlesMissingLoginSuccessCallback = function() {
	this.setupAjaxCall(true);

	this.testObj.init({
		"failure" : this.failureCallback
	});

	verifyZeroInteractions(this.successCallback);
	verifyZeroInteractions(this.failureCallback);
};

FacebookTest.prototype.testHandlesMissingLoginFailureCallback = function() {
	this.setupAjaxCall(false);

	this.testObj.init({
		"success" : this.successCallback
	});

	verifyZeroInteractions(this.successCallback);
	verifyZeroInteractions(this.failureCallback);
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