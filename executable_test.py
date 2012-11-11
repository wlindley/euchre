#!/usr/bin/env python
import mock
import testhelper
import executable
import util

class ExecutableFactoryTest(testhelper.TestCase):
	def setUp(self):
		self.requestDataAccessor = testhelper.createSingletonMock(util.RequestDataAccessor)
		self.responseWriter = testhelper.createSingletonMock(util.ResponseWriter)
		self.testObj = executable.ExecutableFactory.getInstance(self.requestDataAccessor, self.responseWriter)

	def testCallsCreateGameWhenActionIsCreateGame(self):
		createGameExecutable = testhelper.createSingletonMock(executable.CreateGameExecutable)
		action = "createGame"
		self.requestDataAccessor.get.side_effect = lambda k: action if "action" == k else mock.DEFAULT
		result = self.testObj.createExecutable()
		self.assertEqual(createGameExecutable, result)
