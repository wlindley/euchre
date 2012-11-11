from abc import ABCMeta
from abc import abstractmethod
import json

class ExecutableFactory(object):
	instance = None
	@classmethod
	def getInstance(cls, requestDataAccessor, responseWriter):
		if None != cls.instance:
			return cls.instance
		return ExecutableFactory(requestDataAccessor, responseWriter)

	def __init__(self, requestDataAccessor, responseWriter):
		self._requestDataAccessor = requestDataAccessor
		self._responseWriter = responseWriter

	def createExecutable(self):
		action = self._requestDataAccessor.get("action")
		if "createGame" == action:
			return CreateGameExecutable.getInstance(self._requestDataAccessor, self._responseWriter)
		return None

class AbstractExecutable(object):
	__metaclass__ = ABCMeta

	def __init__(self, requestDataAccessor, responseWriter, *args, **kwargs):
		self.requestDataAccessor = requestDataAccessor
		self.responseWriter = responseWriter

	@abstractmethod
	def execute(self, *args, **kwargs):
		return None

class CreateGameExecutable(AbstractExecutable):
	instance = None
	@classmethod
	def getInstance(cls, requestDataAccessor, responseWriter):
		if None != cls.instance:
			return cls.instance
		return CreateGameExecutable(requestDataAccessor, responseWriter)

	def execute(self):
		return json.dumps({})
