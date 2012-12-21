JQueryWrapperTest = TestCase("JQueryWrapperTest")

TestableJQuery = function() {
	this.ajax = function(url, params) {};
};

JQueryWrapperTest.prototype.setUp = function() {
	this.mockJQuery = mock(TestableJQuery);
	this.buildTestObj();
};

JQueryWrapperTest.prototype.testAjaxPassesThrough = function() {
	var url = "my favorite URL";
	var params = {"foo" : "bar", "bin" : "baz"};
	this.testObj.ajax(url, params);
	var paramMatchers = [];
	for (var key in params) {
		paramMatchers.push(hasMember(key, equalTo(params[key])));
	}
	verify(this.mockJQuery).ajax(url, allOf(paramMatchers));
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

JQueryWrapperTest.prototype.buildTestObj = function() {
	this.testObj = AVOCADO.JQueryWrapper.getInstance(this.mockJQuery);
};
