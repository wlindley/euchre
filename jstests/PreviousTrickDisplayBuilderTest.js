PreviousTrickDisplayBuilderTest = TestCase("PreviousTrickDisplayBuilderTest");

PreviousTrickDisplayBuilderTest.prototype.setup = function() {
	this.locStrings = {};
	this.playerId = "12345";

	this.players = [this.playerId, "2", "3", "4"];
	this.cards = [{"suit" : 0, "value" : 9}, {"suit" : 1, "value" : 12}, {"suit" : 1, "value" : 13}, {"suit" : 2, "value" : 10}];
	this.cardHtmls = ["card 1", "card 2", "card 3", "card 4"];
	this.previousTrick = {};
	for (var i in this.players) {
		this.previousTrick[this.players[i]] = this.cards[i];
	}

	this.templateRenderer = mock(AVOCADO.TemplateRenderer);
	this.jqueryWrapper = mock(AVOCADO.JQueryWrapper);

	this.buildTestObj();
	this.doTraining)();
};

PreviousTrickDisplayBuilderTest.prototype.doTraining = function() {
	for (var i in this.cards) {
		when(this.templateRenderer).renderTemplate("card", this.cards[i]).thenReturn(this.cardHtmls[i]);
	}
};

PreviousTrickDisplayBuilderTest.prototype.buildTestObj = function() {
	this.testObj = AVOCADO.PreviousTrickDisplayBuilder.getInstance(this.templateRenderer, this.jqueryWrapper, this.locStrings, this.playerId);
};