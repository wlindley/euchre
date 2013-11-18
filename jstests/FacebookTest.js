FacebookTest = TestCase("FacebookTest");

FakeFB = function() {
	this.init = function() {};
	this.login = function() {};
};

FacebookTest.prototype.setUp = function() {
	this.jqueryWrapper = mock(AVOCADO.JQueryWrapper);
	this.appId = "234023984";
	this.channelUrl = "http://my.awesome.com/channel.html";

	this.buildTestObj();
};

FacebookTest.prototype.tearDown = function() {
	FB = undefined;
};

FacebookTest.prototype.buildTestObj = function() {
	this.testObj = AVOCADO.Facebook.getInstance(this.jqueryWrapper, this.appId, this.channelUrl);	
};

FacebookTest.prototype.setupAjaxCall = function() {
	this.jqueryWrapper.ajax = function(url, params) {
		FB = mock(FakeFB);
		params["success"]();
	};
};

FacebookTest.prototype.testInitLoadsFBScript = function() {
	this.testObj.init();
	verify(this.jqueryWrapper).ajax("//connect.facebook.net/en_US/all.js", allOf(
		hasMember("dataType", "script"),
		hasMember("success", this.testObj.handleAjaxResponse),
		hasMember("cache", true)
	));
};

FacebookTest.prototype.testHandleAjaxResponseInitializesFB = function() {
	this.setupAjaxCall();

	this.testObj.init();
	verify(FB).init(allOf(
		hasMember("appId", this.appId),
		hasMember("channelUrl", this.channelUrl),
		hasMember("status", true),
		hasMember("cookie", true)
	));
};

FacebookTest.prototype.testHandleAjaxResponseLogsIn = function() {
	this.setupAjaxCall();

	this.testObj.init();

	verify(FB).login();
};

FacebookTest.prototype.testHandAjaxResponseInitsBeforeLoggingIn = function() {
	FB = mock(FakeFB);
	this.jqueryWrapper.ajax = function(url, params) {
		params["success"]();
	};
	when(FB).init().thenThrow("Exception!");

	try {
		this.testObj.init();
	} catch (e) {
		//ignore
	}

	verify(FB).init();
	verify(FB, never()).login();
};