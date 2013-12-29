if (AVOCADO == undefined) {
	var AVOCADO = {};
}

AVOCADO.isObjectEmpty = function(obj) {
	if (undefined == obj) {
		return false;
	} else {
		for (var i in obj) {
			return true;
		}
	}
	return false;
}