from pymongo import MongoClient, DESCENDING
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
			self.collections[collection].create_index([('timestamp', DESCENDING)])

	def insertItems(self, collection, items):
		if len(items) == 0:
			return None
		return (self.collections[collection]).insert_one(items[0])

	def queryItems(self, collection, query = {}, sort = [('_id', 1)]):
		return self.collections[collection].find(query).sort(sort)

	def clearCollection(self, collection):
		self.collections[collection].delete_many({})

	def clearDatabase(self):
		for collection in self.collections:
			self.clearCollection(collection)


if __name__ == '__main__':
	posts = [{
	  "author": "Mike",
	  "text": "My first blog post!",
	  "tags": ["mongodb", "python", "pymongo"]
	}, {
	  "author": "Zeu",
	  "text": "My first blog post!",
	  "tags": ["mongos", "java"]
	}]

	# db = Database()
	# db.insertItems('submissions', posts)
	# for s in db.queryItems('submissions'):
	# 	pprint(s)
	# db.clearCollection('submissions')
	# for s in db.queryItems('submissions'):
	# 	pprint(s)


