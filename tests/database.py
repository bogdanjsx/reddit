import unittest
import src.database as database
from pprint import pprint

class DatabaseTest(unittest.TestCase):
	def setUp(self):
		"""Set up database"""
		self.db = database.Database('testing', ['tdd'])

	def testInsert(self):
		"""It should insert the items in the database."""
		items = [{
			'foo': 'bar'
		}, {
			'brebex': 'tdd'
		}]

		self.db.insertItems('tdd', items)
		result = list(self.db.queryItems('tdd'))

		self.assertEqual(result, items, 'Items not inserted properly')

	def testEmptyInsert(self):
		"""Empty inserts should work."""
		self.db.insertItems('tdd', [])
		result = list(self.db.queryItems('tdd'))

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

		self.db.insertItems('tdd', items)
		self.db.clearCollection('tdd')
		result = list(self.db.queryItems('tdd'))

		self.assertEqual(result, [], 'Items not deleted properly')

	def tearDown(self):
		self.db.clearDatabase()

if __name__ == '__main__':
	unittest.main()