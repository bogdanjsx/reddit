import unittest
import src.database as database
import pymongo

class DatabaseTest(unittest.TestCase):
	def setUp(self):
		"""Set up database"""
		self.dbName = 'testing'
		self.db = database.Database(self.dbName, ['tdd'])
		self.mongo = pymongo.MongoClient()

	def testInsert(self):
		"""It should insert the items in the database."""
		items = [{
			'foo': 'bar'
		}, {
			'brebex': 'tdd'
		}]

		self.db.insertItems('tdd', items)
		result = list(self.mongo[self.dbName].tdd.find())

		self.assertEqual(result, items, 'Items not inserted properly')

	def testEmptyInsert(self):
		"""Empty inserts should work."""
		self.db.insertItems('tdd', [])
		result = list(self.mongo[self.dbName].tdd.find())

		self.assertEqual(result, [], 'Empty insert not working')

	def testInvalidCollectionInsert(self):
		"""Inserting into invalid collections should not throw exceptions."""
		items = [{
			'foo': 'bar'
		}, {
			'brebex': 'tdd'
		}]

		self.db.insertItems('agile', items)

		self.assert_(True)

	def testClear(self):
		"""It should clear the collection """
		items = [{
			'foo': 'bar'
		}, {
			'brebex': 'tdd'
		}]

		self.mongo[self.dbName].tdd.insert(items)
		self.db.clearCollection('tdd')
		result = list(self.mongo[self.dbName].tdd.find())

		self.assertEqual(result, [], 'Items not deleted properly')

	def tearDown(self):
		"""Drop the database (no pun intended)"""
		self.mongo.drop_database(self.dbName)

def test_run():
	unittest.main(exit = False)

if __name__ == '__main__':
	test_run()