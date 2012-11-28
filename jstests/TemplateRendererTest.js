TemplateRendererTest = TestCase("TemplateRendererTest")

TemplateRendererTest.prototype.setUp = function() {
	this.templateId = "foo";
	this.template = "my name is %name%";
	this.templates = {};
	this.templates[this.templateId] = this.template;
	this.testObj = new AVOCADO.TemplateRenderer(this.templates);
};

TemplateRendererTest.prototype.testRenderTemplateReplacesDataAndReturns = function() {
	var name = "wlindley";
	var values = {"name" : name};

	var result = this.testObj.renderTemplate(this.templateId, values);

	assertEquals(this.template.replace("%name%", name), result);
};
