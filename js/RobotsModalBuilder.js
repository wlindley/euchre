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

AVOCADO.AddRobotsModalBuilder = function(templateRenderer, jqueryWrapper, playerNameDirectory, dataRetriever, ajax, viewManager) {
	this.buildAddRobotsModal = function(teams, gameId) {
		var modalElement = buildModalElement(teams);
		hookUpNamePromises(modalElement, teams);

		var deferred = jqueryWrapper.buildDeferred();
		deferred.done(buildConfirmClickHandler(gameId, modalElement))
		
		initializeUIElements(modalElement, deferred);

		return AVOCADO.AddRobotsModal.getInstance(modalElement);
	};

	function buildModalElement(teams) {
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
		return jqueryWrapper.getElement(modalHtml);
	}

	function hookUpNamePromises(modalElement, teams) {
		for (var teamId = 0; teamId < 2; teamId++) {
			for (var teamIndex = 0; teamIndex < 2; teamIndex++) {
				var pid = teams[teamId][teamIndex];
				var promise = playerNameDirectory.getNamePromise(pid);
				promise.registerForUpdates(modalElement.find(".playerName").has("input.team[value=" + teamId + "]").has("input.index[value=" + teamIndex + "]"));
			}
		}
	}

	function initializeUIElements(modalElement, deferred) {
		modalElement.modal("setting", {
			"duration" : 200,
			"closable" : false,
			"onApprove" : deferred.resolve,
			"onDeny" : deferred.reject
		});
		modalElement.find(".ui.dropdown").dropdown();
	}

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
	}

	function buildConfirmClickHandler(gameId, modalElement) {
		return function(event) {
			var robotTypesJson = '[[%00%, %01%], [%10%, %11%]]';
			for (var teamId = 0; teamId < 2; teamId++) {
				for (var teamIndex = 0; teamIndex < 2; teamIndex++) {
					//need to start with menu, not input
					var val = modalElement.find(".addRobotsDropdown").has("input.team[value=" + teamId + "]").has("input.index[value=" + teamIndex + "]").find(".addRobotsInput").val();
					if (val) {
						robotTypesJson = robotTypesJson.replace("%" + teamId + teamIndex + "%", '"' + val + '_' + teamId + '_' + teamIndex + '"');
					} else {
						robotTypesJson = robotTypesJson.replace("%" + teamId + teamIndex + "%", 'null');
					}
				}
			}
			ajax.call("addRobots", {"gameId" : gameId, "types" : robotTypesJson}).done(handleAjaxResponse);
		};
	}

	function handleAjaxResponse(response) {
		setTimeout(function() {
			viewManager.showView("gameList");
		}, 100);
	}
};

AVOCADO.AddRobotsModalBuilder.getInstance = function(templateRenderer, jqueryWrapper, playerNameDirectory, dataRetriever, ajax, viewManager) {
	return new AVOCADO.AddRobotsModalBuilder(templateRenderer, jqueryWrapper, playerNameDirectory, dataRetriever, ajax, viewManager);
};