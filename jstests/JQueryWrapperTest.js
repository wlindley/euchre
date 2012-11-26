JQueryWrapperTest = TestCase("JQueryWrapperTest")

TestableJQuery = function() {
	this.ajax = function(url, params) {};
};

JQueryWrapperTest.prototype.setUp = function() {
	this.mockJQuery = mock(TestableJQuery);
	this.testObj = JQueryWrapper.getInstance(this.mockJQuery);
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
