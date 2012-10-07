import unittest
import mock

classesToRemoveInstancesFrom = []

def createMock(cls):
	return mock.create_autospec(cls)

def createSingletonMock(cls):
	if None != cls.instance:
		return cls.instance
	cls.instance = mock.create_autospec(cls)
	classesToRemoveInstancesFrom.append(cls)
	return cls.instance

def destroySingletonMocks():
	for cls in classesToRemoveInstancesFrom:
		if "instance" in cls.__dict__:
			cls.instance = None

class TestCase(unittest.TestCase):
	def tearDown(self):
		destroySingletonMocks()
