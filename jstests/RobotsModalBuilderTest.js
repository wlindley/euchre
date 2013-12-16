RobotsModalBuilderTest = TestCase("RobotsModalBuilderTest");

RobotsModalBuilderTest.prototype.setUp = function() {
	this.teams = [["392349098", "2039482347"], ["23948795", "29348729384"]];

	this.addRobotsModal = new AVOCADO.AddRobotsModal();
	this.addRobotsModalHtml = "so modal, such html";
	this.addRobotsModalElement = mock(TEST.FakeJQueryElement);
	this.addRobotsModalDropdownElement = mock(TEST.FakeJQueryElement);
	this.modalDeferred = mock(TEST.FakeDeferred);
	this.modalPromise = mock(TEST.FakePromise);

	this.origModalGetInstance = AVOCADO.AddRobotsModal.getInstance;
	AVOCADO.AddRobotsModal.getInstance = mockFunction();

	this.templateRenderer = mock(AVOCADO.TemplateRenderer);
	this.jqueryWrapper = mock(AVOCADO.JQueryWrapper);

	this.doTraining();
	this.buildTestObj();
};

RobotsModalBuilderTest.prototype.tearDown = function() {
	AVOCADO.AddRobotsModal.getInstance = this.origModalGetInstance;
};

RobotsModalBuilderTest.prototype.buildTestObj = function() {
	this.testObj = new AVOCADO.AddRobotsModalBuilder(this.templateRenderer, this.jqueryWrapper);
};

RobotsModalBuilderTest.prototype.doTraining = function() {
	when(AVOCADO.AddRobotsModal.getInstance)(this.addRobotsModalElement).thenReturn(this.addRobotsModal);
	when(this.jqueryWrapper).buildDeferred().thenReturn(this.modalDeferred);
	when(this.modalDeferred).promise().thenReturn(this.modalPromise);

	when(this.addRobotsModalElement).find(".ui.dropdown").thenReturn(this.addRobotsModalDropdownElement);

	when(this.templateRenderer).renderTemplate("addRobotsModal").thenReturn(this.addRobotsModalHtml);
	when(this.jqueryWrapper).getElement(this.addRobotsModalHtml).thenReturn(this.addRobotsModalElement);
};

RobotsModalBuilderTest.prototype.trigger = function() {
	return this.testObj.buildAddRobotsModal(this.teams);
};

RobotsModalBuilderTest.prototype.testBuildReturnsExpectedValue = function() {
	var result = this.trigger();
	assertEquals(this.addRobotsModal, result);
};

RobotsModalBuilderTest.prototype.testBuildInitializesModalAndDropdowns = function() {
	this.trigger();

	verify(this.addRobotsModalElement).modal("setting", allOf(
		hasMember("duration", 200),
		hasMember("closable", false),
		hasMember("onApprove", this.modalDeferred.resolve),
		hasMember("onDeny", this.modalDeferred.reject)
	));
	verify(this.addRobotsModalDropdownElement).dropdown();
};

RobotsModalBuilderTest.prototype.testModalGetElementReturnsExpectedElement = function() {
	AVOCADO.AddRobotsModal.getInstance = this.origModalGetInstance;
	var result = this.trigger();
	assertEquals(this.addRobotsModalElement, result.getElement());
};

RobotsModalBuilderTest.prototype.testModalShowDisplaysModal = function() {
	AVOCADO.AddRobotsModal.getInstance = this.origModalGetInstance;
	var result = this.trigger();
	result.show();
	verify(this.addRobotsModalElement).modal("show");
};