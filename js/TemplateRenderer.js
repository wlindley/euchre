if (AVOCADO == undefined) {
	var AVOCADO = {};
}

AVOCADO.TemplateRenderer = function(templates) {
	var self = this;

	this.renderTemplate = function(templateId, values) {
		var template = "";
		if (templateId in templates) {
			template = "" + templates[templateId];
		}
		for (var key in values) {
			template = template.replace(new RegExp("%" + key + "%", "g"), values[key]);
		}
		return template;
	};
};

AVOCADO.TemplateRenderer.getInstance = function(templates) {
	return new AVOCADO.TemplateRenderer(templates);
};
