if (AVOCADO == undefined) {
	var AVOCADO = {};
}

AVOCADO.TemplateRenderer = function(dataRetriever) {
	var self = this;

	this.renderTemplate = function(templateId, values) {
		var templates = dataRetriever.get("templates");
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

AVOCADO.TemplateRenderer.getInstance = function(dataRetriever) {
	return new AVOCADO.TemplateRenderer(dataRetriever);
};
