#!/usr/bin/env python
import testhelper
import unittest
import mock
import serializer
import game
import euchre

class PlayerSerializerTest(testhelper.TestCase):
	def setUp(self):
		super(PlayerSerializerTest, self).setUp()
		self.testObj = serializer.PlayerSerializer()
		self.playerId = "123"

	def testSerializesPlayerCorrectly(self):
		player = game.Player(self.playerId)
		data = self.testObj.serialize(player)
		self.assertEqual(self.playerId, data["playerId"])

	def testDeserializesPlayerCorrectly(self):
		data = {"playerId" : self.playerId}
		player = self.testObj.deserialize(data)
		self.assertEqual(self.playerId, player.playerId)

if __name__ == "__main__":
	unittest.main()
