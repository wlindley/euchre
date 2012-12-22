if (AVOCADO == undefined) {
	var AVOCADO = {};
}

AVOCADO.ViewManager = function() {
	var self = this;
	var viewMap = {};

	this.registerView = function(viewName, viewObject) {
		viewMap[viewName] = viewObject;
	};

	this.showView = function(viewName, params) {
		for (var key in viewMap) {
			viewMap[key].hide();
		}
		viewMap[viewName].show(params);
	};
};

AVOCADO.ViewManager.getInstance = function() {
	return new AVOCADO.ViewManager();
};
