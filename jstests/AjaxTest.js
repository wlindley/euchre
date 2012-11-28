AjaxTest = TestCase("AjaxTest")

AjaxTest.prototype.setUp = function() {
	this.url = "http://localhost:8080/ajax"
	this.jqueryWrapper = mock(AVOCADO.JQueryWrapper);
	this.testObj = AVOCADO.Ajax.getInstance(this.jqueryWrapper, this.url);
};

AjaxTest.prototype.testCallCallsJQueryAjax = function() {
	var action = "the best action";
	var data = {"foo" : "bar"};
	var callback = function(response) {};
	this.testObj.call(action, data, callback);
	var dataMatchers = [];
	for (var key in data) {
		dataMatchers.push(hasMember(key, data[key]));
	}
	dataMatchers.push(hasMember("action", action));
	var paramMatchers = [hasMember("type", "POST"), hasMember("data", allOf(dataMatchers)), hasMember("success", callback), hasMember("dataType", "json")]
	verify(this.jqueryWrapper).ajax(this.url, allOf(paramMatchers));
};
