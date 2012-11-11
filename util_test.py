#!/usr/bin/env python
import mock
import testhelper
import util

class RequestDataAccessorTest(testhelper.TestCase):
	def setUp(self):
		self.request = mock.MagicMock()
		self.request.get = mock.MagicMock()
		self.testObj = util.RequestDataAccessor.getInstance(self.request)

	def testGetPassesThroughToRequest(self):
		params = "some key"
		expectedResult = "some data"
		self.request.get.side_effect = lambda p: expectedResult if params == p else mock.DEFAULT
		result = self.testObj.get(params)
		self.assertEqual(expectedResult, result)

class ResponseWriterTest(testhelper.TestCase):
	def setUp(self):
		self.response = mock.MagicMock()
		self.response.write = mock.MagicMock()
		self.testObj = util.ResponseWriter.getInstance(self.response)

	def testWritePassesThroughToResponse(self):
		params = "some response"
		self.testObj.write(params)
		self.response.write.assert_called_with(params)
