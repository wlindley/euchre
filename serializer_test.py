#!/usr/bin/env python
import testhelper
import unittest
import mock
import serializer
import game
import euchre
import model

class SerializerTest(testhelper.TestCase):
	def setUp(self):
		super(SerializerTest, self).setUp()
		self.serializer = serializer.Serializer()

	def testSerializesPlayerCorrectly(self):
		player = game.Player("123")
		obj = self.serializer.serialize(player)
		self.assertEqual("123", obj.playerId)

	def testDeserializesPlayerCorrectly(self):
		obj = model.PlayerModel(playerId="123")
		player = self.serializer.deserialize(obj)
		self.assertEqual("123", player.playerId)
