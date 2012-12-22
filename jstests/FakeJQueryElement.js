if (TEST == undefined) {
	var TEST = {};
}

TEST.FakeJQueryElement = function() {
	this.html = function() {};
	this.show = function() {};
	this.hide = function() {};
	this.click = function() {};
	this.val = function() {};
	this.find = function() {};
	this.appendTo = function() {};
	this.attr = function() {};
	this.empty = function() {};
	this.removeClass = function() {};
};
