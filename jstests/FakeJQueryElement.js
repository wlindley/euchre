if (TEST == undefined) {
	var TEST = {};
}

TEST.FakeJQueryElement = function() {
	this.html = function() {};
	this.show = function() {};
	this.click = function() {};
};
