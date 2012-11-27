TemplateRenderer = function(templates) {
	var self = this;

	this.renderTemplate = function(templateId, values) {
		var template = "";
		if (templateId in templates) {
			template = "" + templates[templateId];
		}
		for (var key in values) {
			template = template.replace("%" + key + "%", values[key]);
		}
		return template;
	};
};

TemplateRenderer.getInstance = function(templates) {
	return new TemplateRenderer(templates);
};
