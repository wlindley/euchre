JQueryWrapperTest = TestCase("JQueryWrapperTest")

TestableJQuery = function() {
	this.ajax = function(url, params) {};
	this.Deferred = function() {};
	this.parseJSON = function(json) {};
	this.when = function() {};
};

JQueryWrapperTest.prototype.setUp = function() {
	this.mockJQuery = mock(TestableJQuery);
	this.buildTestObj();
};

JQueryWrapperTest.prototype.testAjaxPassesThrough = function() {
	var promise = mock(TEST.FakePromise);
	var url = "my favorite URL";
	var params = {"foo" : "bar", "bin" : "baz"};

	var paramMatchers = [];
	for (var key in params) {
		paramMatchers.push(hasMember(key, equalTo(params[key])));
	}
	when(this.mockJQuery).ajax(url, allOf(paramMatchers)).thenReturn(promise);

	var result = this.testObj.ajax(url, params);

	assertEquals(promise, result);
};

JQueryWrapperTest.prototype.testGetElementPassesThrough = function() {
	var params = null;
	this.mockJQuery = function(elementOrSelector) {
		params = elementOrSelector;
	};
	this.buildTestObj();

	var selector = "#foo";
	this.testObj.getElement(selector);
	assertEquals(selector, params);
};

JQueryWrapperTest.prototype.testBuildDeferredPassesThrough = function() {
	when(this.mockJQuery).Deferred().thenReturn($.Deferred());
	var result = this.testObj.buildDeferred();
	assertTrue(result.hasOwnProperty("done"));
	assertTrue(result.hasOwnProperty("fail"));
	assertTrue(result.hasOwnProperty("progress"));
	assertTrue(result.hasOwnProperty("resolve"));
	assertTrue(result.hasOwnProperty("reject"));
	assertTrue(result.hasOwnProperty("notify"));
	assertTrue(result.hasOwnProperty("promise"));
};

JQueryWrapperTest.prototype.testJsonDecodePassesThrough = function() {
	var json = '{"foo" : "bar"}';
	var expectedResult = {"foo" : "bar"};
	when(this.mockJQuery).parseJSON(json).thenReturn(expectedResult);
	var result = this.testObj.jsonDecode(json);
	assertEquals(expectedResult, result);
};

JQueryWrapperTest.prototype.testCombinePromisesPassesThrough = function() {
	var deferred1 = mock(TEST.FakeDeferred);
	var deferred2 = mock(TEST.FakeDeferred);
	var promise = mock(TEST.FakePromise);

	when(this.mockJQuery).when(deferred1, deferred2).thenReturn(promise);

	var result = this.testObj.combinePromises(deferred1, deferred2);

	assertEquals(promise, result);
};

JQueryWrapperTest.prototype.buildTestObj = function() {
	this.testObj = AVOCADO.JQueryWrapper.getInstance(this.mockJQuery);
};