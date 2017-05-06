from pymongo import MongoClient, IndexModel, DESCENDING, TEXT
from pprint import pprint

class Database:
	def __init__(self, name, collections):
		self.db = MongoClient()[name]
		self.collections = {
			collection: self.db[collection] for collection in collections
		}
		self.createIndexes()

	def createIndexes(self):
		for collection in self.collections:
			timeIndex = IndexModel([('timestamp', DESCENDING)], name = 'timestamp')
			textIndex = IndexModel(
					[('title', TEXT), ('text', TEXT)],
					default_language = 'english',
					name = 'text',
					sparse = True # Ignore documents that lack this field
			)

			self.collections[collection].create_indexes([
				timeIndex,
				textIndex
			])

	def insertItems(self, collection, items):
		if len(items) == 0:
			return None
		return (self.collections[collection]).insert(items)

	def queryItems(self, collection, query = {}, sort = [('_id', 1)]):
		return self.collections[collection].find(query).sort(sort)

	def clearCollection(self, collection):
		self.collections[collection].delete_many({})

	def clearDatabase(self):
		for collection in self.collections:
			self.clearCollection(collection)
