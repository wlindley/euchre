if (AVOCADO == undefined) {
	AVOCADO = {};
}

AVOCADO.GameListElementBuilder = function(jqueryWrapper, templateRenderer, locStrings, playerNameDirectory, facebook, ajax, viewManager, addRobotsModalBuilder, teamUtils) {
	var self = this;

	this.buildListElement = function(gameData, requestId) {
		var element = buildElement(gameData);
		setupAddRobotsModal(element, gameData);
		setupGameIcons(element, gameData);
		showAddRobotsButton(element, gameData);
		
		addClickHandlers(element, gameData, requestId);

		hookupTurnNamePromise(element, gameData);
		hookupTeamNamePromisesAndClickHandlers(element, gameData, requestId)

		showTeamColors(element, gameData);

		return element;
	};

	function buildElement(gameData) {
		var templateParams = {
			"vs" : locStrings["vs"],
			"gameId" : gameData.gameId,
			"status" : locStrings[gameData.status]
		};
		var elementHtml = templateRenderer.renderTemplate("gameListEntry", templateParams);
		return jqueryWrapper.getElement(elementHtml);
	}

	function setupAddRobotsModal(element, gameData) {
		var addRobotsModal = addRobotsModalBuilder.buildAddRobotsModal(gameData.teams, gameData.gameId);
		var addRobotsButton = element.find(".addRobotsButton");
		element.find(".addRobotsModalContainer").append(addRobotsModal.getElement());
		addRobotsButton.hide();
		addRobotsButton.click(self.buildAddRobotsClickHandler(addRobotsModal));
	}

	function hideGameIcons(element) {
		element.find(".playGame").hide();
		element.find(".joinGame").hide();
		element.find(".inviteToGame").hide();
		element.find(".gameOver").hide();
	}

	function showCorrectGameIcon(element, gameData) {
		if ("waiting_for_more_players" == gameData.status) {
			if (teamUtils.isLocalPlayerInGame(gameData.teams)) {
				element.find(".inviteToGame").show();
			} else {
				element.find(".joinGame").show();
			}
		} else if ("complete" == gameData.status) {
			element.find(".gameOver").show();
		} else if (gameData.currentPlayerId == facebook.getSignedInPlayerId()) {
			element.find(".playGame").show();
		}
	}

	function showAddRobotsButton(element, gameData) {
		if ("waiting_for_more_players" == gameData.status && teamUtils.isLocalPlayerInGame(gameData.teams)) {
			element.find(".addRobotsButton").show();
		}
	}

	function setupGameIcons(element, gameData) {
		hideGameIcons(element);
		showCorrectGameIcon(element, gameData);
	}

	function addClickHandlers(element, gameData, requestId) {
		if ("waiting_for_more_players" == gameData.status) {
			if (teamUtils.isLocalPlayerInGame(gameData.teams)) {
				element.click(self.buildGameInviteClickHandler(gameData.gameId));
			} else {
				var openTeams = teamUtils.findOpenTeams(gameData.teams);
				var teamId = openTeams[Math.floor(Math.random() * openTeams.length)];
				element.click(self.buildGameJoinClickHandler(gameData.gameId, teamId, requestId));
			}
		} else {
			element.click(self.buildShowGameDataHandler(gameData.gameId));
		}
	}

	function hookupTurnNamePromise(element, gameData) {
		var nameElement = element.find(".turn").find(".playerName");
		if (null == gameData.currentPlayerId) {
			nameElement.text(locStrings["n/a"]);
		} else {
			var namePromise = playerNameDirectory.getNamePromise(gameData.currentPlayerId);
			namePromise.registerForUpdates(nameElement);
		}
	}

	function hookupTeamNamePromisesAndClickHandlers(element, gameData, requestId) {
		var playerTable = element.find(".gameListElementTeams");
		for (var teamId = 0; teamId < 2; teamId++) {
			for (var index = 0; index < 2; index++) {
				var dataElement = playerTable.find(".playerNameContainer").has("input.team[value=" + teamId + "]").has("input.index[value=" + index + "]");
				var dataNameElement = dataElement.find(".playerName");
				if ((teamId in gameData.teams) && (index in gameData.teams[teamId])) {
					var namePromise = playerNameDirectory.getNamePromise(gameData.teams[teamId][index]);
					namePromise.registerForUpdates(dataNameElement);
				} else {
					var message = locStrings["inviteCTA"];
					if (!teamUtils.isLocalPlayerInGame(gameData.teams)) {
						message = locStrings["joinCTA"];
						dataElement.click(self.buildGameJoinClickHandler(gameData.gameId, teamId, requestId));
					}
					dataNameElement.text(message);
				}
			}
		}
	}

	function showTeamColors(element, gameData) {
		if (teamUtils.isLocalPlayerOnTeam(gameData.teams[0])) {
			element.find(".team0").addClass(teamUtils.getAllyClass());
			element.find(".team1").addClass(teamUtils.getOpponentClass());
		} else {
			element.find(".team0").addClass(teamUtils.getOpponentClass());
			element.find(".team1").addClass(teamUtils.getAllyClass());
		}
	}

	this.buildShowGameDataHandler = function(gameId) {
		return function(event) {
			viewManager.showView("gamePlay", {"gameId" : gameId});
		};
	};

	this.buildGameInviteClickHandler = function(gameId) {
		return function(event) {
			facebook.sendRequests(locStrings["gameInviteTitle"], locStrings["gameInviteMessage"], {"gameId" : gameId});
		};
	};

	this.buildGameJoinClickHandler = function(gameId, teamId, requestId) {
		return function(event) {
			ajax.call("addPlayer", {
				"gameId" : gameId,
				"team" : teamId,
				"playerId" : facebook.getSignedInPlayerId()
			}).done(self.buildHandleJoinGameResponse(requestId));
		};
	};

	this.buildHandleJoinGameResponse = function(requestId) {
		return function(response) {
			if (response.success) {
				facebook.deleteAppRequest(requestId);
			}
			setTimeout(function() {
				viewManager.showView("gameList");
			}, 100);
		};
	};

	this.buildAddRobotsClickHandler = function(modal) {
		return function(event) {
			event.stopPropagation();
			modal.show();
		};
	};
};

AVOCADO.GameListElementBuilder.getInstance = function(jqueryWrapper, templateRenderer, locStrings, playerNameDirectory, facebook, ajax, viewManager, dataRetriever, teamUtils) {
	var modalBuilder = AVOCADO.AddRobotsModalBuilder.getInstance(templateRenderer, jqueryWrapper, playerNameDirectory, dataRetriever, ajax, viewManager);
	return new AVOCADO.GameListElementBuilder(jqueryWrapper, templateRenderer, locStrings, playerNameDirectory, facebook, ajax, viewManager, modalBuilder, teamUtils);
};