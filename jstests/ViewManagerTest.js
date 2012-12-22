ViewManagerTest = TestCase("ViewManagerTest");

if (TEST == undefined) {
	var TEST = {};
}

TEST.FakeView = function() {
	this.show = function() {};
	this.hide = function() {};
};

ViewManagerTest.prototype.setUp = function() {
	this.views = {
		"view1" : mock(TEST.FakeView),
		"view2" : mock(TEST.FakeView),
		"view3" : mock(TEST.FakeView)
	};
	this.buildTestObj();
};

ViewManagerTest.prototype.testRegisterAndShowWorkAsExpected = function() {
	for (var key in this.views) {
		this.testObj.registerView(key, this.views[key]);
	}
	
	var params1 = {"foo" : "bar", "bin" : "baz"};
	this.testObj.showView("view1", params1);
	for (var key in this.views) {
		verify(this.views[key]).hide();
	}
	verify(this.views["view1"]).show(allOf(hasMember("foo", "bar"), hasMember("bin", "baz")));

	var params2 = {1 : "bing", 2 : "bam", 4 : "scram"};
	this.testObj.showView("view3", params2);
	for (var key in this.views) {
		verify(this.views[key], times(2)).hide();
	}
	verify(this.views["view3"]).show(allOf(hasMember(1, "bing"), hasMember(2, "bam"), hasMember(4, "scram")));
};

ViewManagerTest.prototype.buildTestObj = function() {
	this.testObj = new AVOCADO.ViewManager();
};
