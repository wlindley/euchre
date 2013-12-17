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

AVOCADO.AddRobotsModalBuilder = function(templateRenderer, jqueryWrapper, playerNameDirectory) {
	this.buildAddRobotsModal = function(teams) {
		var templateParams = {};
		for (var teamId = 0; teamId < 2; teamId++) {
			for (var teamIndex = 0; teamIndex < 2; teamIndex++) {
				var templateName = "addRobotsExistingPlayer";
				if (undefined === teams[teamId][teamIndex]) {
					templateName = "addRobotsMenu";
				}
				templateParams["team" + teamId + "_player" + teamIndex] = templateRenderer.renderTemplate(templateName, {"teamId" : teamId, "teamIndex" : teamIndex});
			}
		}

		var modalHtml = templateRenderer.renderTemplate("addRobotsModal", templateParams);
		var modalElement = jqueryWrapper.getElement(modalHtml);

		for (var teamId = 0; teamId < 2; teamId++) {
			for (var teamIndex = 0; teamIndex < 2; teamIndex++) {
				var pid = teams[teamId][teamIndex];
				var promise = playerNameDirectory.getNamePromise(pid);
				promise.registerForUpdates(modalElement.find(".playerName").has("input.team[value=" + teamId + "]").has("input.index[value=" + teamIndex + "]"));
			}
		}

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

AVOCADO.AddRobotsModalBuilder.getInstance = function(templateRenderer, jqueryWrapper, playerNameDirectory) {
	return new AVOCADO.AddRobotsModalBuilder(templateRenderer, jqueryWrapper, playerNameDirectory);
};