if (AVOCADO == undefined) {
	AVOCADO = {};
}

AVOCADO.DataRetriever = function(dataObj) {
	this.get = function(key) {
		return dataObj[key];
	};
};

AVOCADO.DataRetriever.getInstance = function(dataObj) {
	return new AVOCADO.DataRetriever(dataObj);
};