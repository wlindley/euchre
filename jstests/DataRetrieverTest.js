DataRetrieverTest = TestCase("DataRetrieverTest");

DataRetrieverTest.prototype.setUp = function() {
	this.pageData = {
		"foo" : 3209,
		"bar" : "dlakjf",
		"baz" : {"one" : "two"}
	};
	this.buildTestObj();
};

DataRetrieverTest.prototype.buildTestObj = function() {
	this.testObj = new AVOCADO.DataRetriever(this.pageData);
};

DataRetrieverTest.prototype.testGetReturnsExpectedValues = function() {
	var keys = ["foo", "bar", "baz"];
	for (var i in keys) {
		assertEquals(this.pageData[keys[i]], this.testObj.get(keys[i]));
	}
};

DataRetrieverTest.prototype.testGetReturnsNullWhenKeyNotPresent = function() {
	assertEquals(null, this.testObj.get("bing"));
};