import pymongo

DESCENDING = pymongo.DESCENDING

class Database(object):
	"""Database abstraction class. Provides an interface for CRUD operations on an
			internal database."""
	def __init__(self, name, collections, createIndexes = True):
		"""Connects to the underlying database and performs initializations."""
		self.db = pymongo.MongoClient()[name]
		self.collections = {
			collection: self.db[collection] for collection in collections
		}

		if createIndexes:
			self.createIndexes()

	def createIndexes(self):
		"""Create indexes on the database for faster queries."""

		for collection in self.collections:
			timeIndex = pymongo.IndexModel([('timestamp', DESCENDING)], name = 'timestamp')
			textIndex = pymongo.IndexModel(
				[('title', pymongo.TEXT), ('text', pymongo.TEXT)],
				default_language = 'english',
				name = 'text',
				sparse = True # Ignore documents that lack this field
			)

			self.collections[collection].create_indexes([
				timeIndex,
				textIndex
			])

	def insertItems(self, collection, items):
		"""Inserts items into collection."""
		if len(items) == 0 or collection not in self.collections:
			return []

		return (self.collections[collection]).insert(items)

	def queryItems(self, collection, query = {}, sort = [('_id', 1)]):
		"""Performs the query on collection."""
		if collection not in self.collections:
			return []

		return self.collections[collection].find(query).sort(sort)

	def clearCollection(self, collection):
		"""Fully empties the collection."""
		self.collections[collection].delete_many({})

	def clearDatabase(self):
		"""Fully empties all the collections in the database."""
		for collection in self.collections:
			self.clearCollection(collection)
