TrumpSelectionAreaBuilder = TestCase("TrumpSelectionAreaBuilder");

TrumpSelectionAreaBuilder.prototype.setUp = function() {
	this.templateRenderer = mock(AVOCADO.TemplateRenderer);
	this.buildTestObj();
};

TrumpSelectionAreaBuilder.prototype.testBuildReturnsCorrectResult = function() {
	var upCard = {"suit" : 1, "value" : 10};
	var upCardHtml = "up card html";
	when(this.templateRenderer).renderTemplate("card", allOf(hasMember("suit", upCard.suit), hasMember("value", upCard.value))).thenReturn(upCardHtml);

	var trumpSelectionHtml = "trump selection section";
	when(this.templateRenderer).renderTemplate("trumpSelection", hasMember("card", upCardHtml)).thenReturn(trumpSelectionHtml);

	var actualResult = this.testObj.buildTrumpSelectionArea(upCard);
	assertEquals(trumpSelectionHtml, actualResult);
};

TrumpSelectionAreaBuilder.prototype.testBuildReturnsEmptyStringWhenUpCardIsNull = function() {
	var upCard = null;
	assertEquals("", this.testObj.buildTrumpSelectionArea(upCard));
};

TrumpSelectionAreaBuilder.prototype.buildTestObj = function() {
	this.testObj = new AVOCADO.TrumpSelectionAreaBuilder(this.templateRenderer);
};
