if (AVOCADO == undefined) {
	AVOCADO = {};
}

AVOCADO.AddRobotsModal = function(modalElement) {
	this.getElement = function() {
		return modalElement;
	};

	this.show = function() {
		modalElement.modal("show");
	};
};

AVOCADO.AddRobotsModal.getInstance = function(modalElement) {
	return new AVOCADO.AddRobotsModal(modalElement);
};

AVOCADO.AddRobotsModalBuilder = function(templateRenderer, jqueryWrapper) {
	this.buildAddRobotsModal = function(teams) {
		var modalHtml = templateRenderer.renderTemplate("addRobotsModal");
		var modalElement = jqueryWrapper.getElement(modalHtml);
		var deferred = jqueryWrapper.buildDeferred();

		modalElement.modal("setting", {
			"duration" : 200,
			"closable" : false,
			"onApprove" : deferred.resolve,
			"onDeny" : deferred.reject
		});
		modalElement.find(".ui.dropdown").dropdown();

		return AVOCADO.AddRobotsModal.getInstance(modalElement);
	};
};

AVOCADO.AddRobotsModalBuilder.getInstance = function(templateRenderer, jqueryWrapper) {
	return new AVOCADO.AddRobotsModalBuilder(templateRenderer, jqueryWrapper);
};