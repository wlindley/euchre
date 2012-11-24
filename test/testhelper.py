import unittest
from mockito import *

classesToRemoveInstancesFrom = []
classesToRestore = {}

def createSimpleMock():
	return mock()

def createMock(cls):
	return mock(cls)

def createSingletonMock(cls):
	if None != cls.instance:
		return cls.instance
	cls.instance = createMock(cls)
	classesToRemoveInstancesFrom.append(cls)
	return cls.instance

def replaceClass(module, classname, mockObj):
	if classname not in module.__dict__:
		return
	if module not in classesToRestore:
		classesToRestore[module] = {}
	classesToRestore[module][classname] = module.__dict__[classname]
	module.__dict__[classname] = mockObj

def destroySingletonMocks():
	for cls in classesToRemoveInstancesFrom:
		if "instance" in cls.__dict__:
			cls.instance = None

def restoreClasses():
	for module, classes in classesToRestore.iteritems():
		for classname, cls in classes.iteritems():
			module.__dict__[classname] = cls

class TestCase(unittest.TestCase):
	def setUp(self):
		super(TestCase, self).setUp()

	def tearDown(self):
		destroySingletonMocks()
		restoreClasses()
		super(TestCase, self).tearDown()
