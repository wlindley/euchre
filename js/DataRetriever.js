if (AVOCADO == undefined) {
	AVOCADO = {};
}

AVOCADO.DataRetriever = function(dataObj) {
	this.get = function(key) {
		throw "Not Yet Implemented";
	};
};

AVOCADO.DataRetriever.getInstance = function(dataObj) {
	return new DataRetriever(dataObj);
};