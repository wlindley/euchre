import unittest
from mockito import *

classesToRemoveInstancesFrom = []

def createMock(cls):
	return mock(cls)

def createSingletonMock(cls):
	if None != cls.instance:
		return cls.instance
	cls.instance = createMock(cls)
	classesToRemoveInstancesFrom.append(cls)
	return cls.instance

def destroySingletonMocks():
	for cls in classesToRemoveInstancesFrom:
		if "instance" in cls.__dict__:
			cls.instance = None

class TestCase(unittest.TestCase):
	def setUp(self):
		super(TestCase, self).setUp()

	def tearDown(self):
		destroySingletonMocks()
		super(TestCase, self).tearDown()
