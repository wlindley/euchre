TemplateRendererTest = TestCase("TemplateRendererTest")

TemplateRendererTest.prototype.setUp = function() {
	this.templateId = "foo";
	this.template = "my name is %name% %name%";
	this.templates = {};
	this.templates[this.templateId] = this.template;

	this.dataRetriever = mock(AVOCADO.DataRetriever);
	when(this.dataRetriever).get("templates").thenReturn(this.templates);

	this.testObj = new AVOCADO.TemplateRenderer(this.dataRetriever);
};

TemplateRendererTest.prototype.testRenderTemplateReplacesDataAndReturns = function() {
	var name = "wlindley";
	var values = {"name" : name};

	var result = this.testObj.renderTemplate(this.templateId, values);

	assertEquals(this.template.replace(/%name%/g, name), result);
};
