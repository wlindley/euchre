class RequestDataAccessor(object):
	instance = None
	@classmethod
	def getInstance(cls, request):
		if None != cls.instance:
			return cls.instance
		return RequestDataAccessor(request)

	def __init__(self, request):
		self._request = request

	def get(self, key):
		return self._request.get(key)

class ResponseWriter(object):
	instance = None
	@classmethod
	def getInstance(cls, response):
		if None != cls.instance:
			return cls.instance
		return ResponseWriter(response)

	def __init__(self, response):
		self._response = response

	def write(self, data):
		self._response.write(data)