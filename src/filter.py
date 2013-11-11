from google.appengine.ext import ndb
import model

class BaseFilter(object):
	instance = None
	@classmethod
	def getInstance(cls):
		if None != cls.instance:
			return cls.instance
		return BaseFilter()

	def filterItem(self, item):
		return True

	def filterList(self, items):
		return filter(self.filterItem, items)

class PlayerHasNotRemovedGameModelFilter(BaseFilter):
	instance = None
	@classmethod
	def getInstance(cls, playerId):
		if None != cls.instance:
			return cls.instance
		return PlayerHasNotRemovedGameModelFilter(playerId)

	def __init__(self, playerId):
		super(PlayerHasNotRemovedGameModelFilter, self).__init__()
		self._playerId = playerId

	def filterItem(self, item):
		return not self._playerId in item.readyToRemove