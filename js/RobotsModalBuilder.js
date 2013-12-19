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

AVOCADO.AddRobotsModalBuilder = function(templateRenderer, jqueryWrapper, playerNameDirectory, dataRetriever) {
	this.buildAddRobotsModal = function(teams) {
		var templateParams = {};
		for (var teamId = 0; teamId < 2; teamId++) {
			for (var teamIndex = 0; teamIndex < 2; teamIndex++) {
				var paramId = "team" + teamId + "_player" + teamIndex;
				if (undefined === teams[teamId][teamIndex]) {
					templateParams[paramId] = buildRobotsMenu(teamId, teamIndex);
				} else {
					templateParams[paramId] = templateRenderer.renderTemplate("addRobotsExistingPlayer", {"teamId" : teamId, "teamIndex" : teamIndex});
				}
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

	function buildRobotsMenu(teamId, teamIndex) {
		var robotData = dataRetriever.get("robots");
		var defaultId = "";
		var defaultDisplayName = "";
		var robotTypeListHtml = "";

		for (var i in robotData) {
			if (robotData[i].default) {
				defaultId = robotData[i].id;
				defaultDisplayName = robotData[i].displayName;
			}
			robotTypeListHtml += templateRenderer.renderTemplate("addRobotsMenuElement", {"id" : robotData[i].id, "displayName" : robotData[i].displayName});
		}
		return templateRenderer.renderTemplate("addRobotsMenu", {
			"teamId" : teamId,
			"teamIndex" : teamIndex,
			"defaultId" : defaultId,
			"defaultDisplayName" : defaultDisplayName,
			"robotList" : robotTypeListHtml
		});
	};
};

AVOCADO.AddRobotsModalBuilder.getInstance = function(templateRenderer, jqueryWrapper, playerNameDirectory, dataRetriever) {
	return new AVOCADO.AddRobotsModalBuilder(templateRenderer, jqueryWrapper, playerNameDirectory, dataRetriever);
};