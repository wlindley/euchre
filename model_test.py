#!/usr/bin/env python

import mock
import testhelper
#patchers = []
#patchers.append(mock.patch("google.appengine.ext.db.Model"))
#patchers.append(mock.patch("google.appengine.ext.db.StringProperty"))
#patchers.append(mock.patch("google.appengine.ext.db.TextProperty"))
#patchers.append(mock.patch("google.appengine.api.datastore"))
#patchers.append(mock.patch("model.db.Model"))
#patchers.append(mock.patch("model.db.StringProperty"))
#patchers.append(mock.patch("model.db.TextProperty"))
#for patcher in patchers:
	#patcher.start()

import model

class ModelTest(testhelper.TestCase):
	def setUp(self):
		pass

	def test123(self):
		self.assertTrue(True)

#for patcher in patchers:
	#patcher.stop()
