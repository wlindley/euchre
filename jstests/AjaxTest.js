AjaxTest = TestCase("AjaxTest")

AjaxTest.prototype.setUp = function() {
	this.url = "http://localhost:8080/ajax"
	this.jqueryWrapper = mock(AVOCADO.JQueryWrapper);
	this.ajaxPromise = mock(TEST.FakePromise);

	this.action = "the best action";
	this.data = {"foo" : "bar"};

	this.dataMatchers = [];
	for (var key in this.data) {
		this.dataMatchers.push(hasMember(key, this.data[key]));
	}
	this.dataMatchers.push(hasMember("action", this.action));
	this.paramMatchers = [hasMember("type", "POST"), hasMember("data", allOf(this.dataMatchers)), hasMember("dataType", "json")];

	this.doTraining();
	this.buildTestObj();
};

AjaxTest.prototype.buildTestObj = function() {
	this.testObj = AVOCADO.Ajax.getInstance(this.jqueryWrapper, this.url);
};

AjaxTest.prototype.doTraining = function() {
	when(this.jqueryWrapper).ajax(this.url, allOf(this.paramMatchers)).thenReturn(this.ajaxPromise);
};

AjaxTest.prototype.trigger = function() {
	return this.testObj.call(this.action, this.data);
};

AjaxTest.prototype.testCallReturnsExpectedPromise = function() {
	var result = this.trigger();
	assertEquals(this.ajaxPromise, result);
};