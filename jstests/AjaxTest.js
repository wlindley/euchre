AjaxTest = TestCase("AjaxTest")

AjaxTest.prototype.setUp = function() {
	this.url = "http://localhost:8080/ajax"
	this.jqueryWrapper = mock(AVOCADO.JQueryWrapper);

	this.action = "the best action";
	this.data = {"foo" : "bar"};
	this.callback = function(response) {};
	this.origSetTimeout = setTimeout;
	setTimeout = function(func, time, lang) {
		func();
	};

	this.dataMatchers = [];
	for (var key in this.data) {
		this.dataMatchers.push(hasMember(key, this.data[key]));
	}
	this.dataMatchers.push(hasMember("action", this.action));
	this.paramMatchers = [hasMember("type", "POST"), hasMember("data", allOf(this.dataMatchers)), hasMember("success", this.callback), hasMember("dataType", "json")]

	this.testObj = AVOCADO.Ajax.getInstance(this.jqueryWrapper, this.url);
};

AjaxTest.prototype.tearDown = function() {
	setTimeout = this.origSetTimeout;
};

AjaxTest.prototype.testCallCallsJQueryAjax = function() {
	var hasCalledAsync = false;
	setTimeout = function(func, time, lang) {
		func();
		hasCalledAsync = true;
	}
	this.testObj.call(this.action, this.data, this.callback);
	verify(this.jqueryWrapper).ajax(this.url, allOf(this.paramMatchers));
	assertFalse(hasCalledAsync);
};

AjaxTest.prototype.testCallDelaysAjaxWithParam = function() {
	var hasCalledAsync = false;
	var calledDelay = -1;
	setTimeout = function(func, time, lang) {
		func();
		hasCalledAsync = true;
		calledDelay = time;
	}
	var time = 5;
	this.testObj.call(this.action, this.data, this.callback, time);
	verify(this.jqueryWrapper).ajax(this.url, allOf(this.paramMatchers));
	assertTrue(hasCalledAsync);
	assertEquals(time, calledDelay);
};