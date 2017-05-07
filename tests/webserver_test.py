import json
import pymongo
import src.webserver as webserver
import unittest

class RedditQueryTest(unittest.TestCase):
	def setUp(self):
		"""Set up web server."""
		self.dbName = 'testing'
		self.mongo = pymongo.MongoClient()

		self.server = webserver.app.test_client()

		with open('tests/test_config.json') as configFile:
			configData = json.load(configFile)
		webserver.initDatabase(configData)

		self.items = [{
			'_id': 0,
			'text': 'foo',
			'timestamp': 5
		}, {
			'_id': 1,
			'title': 'bar',
			'timestamp': 9
		}]
		self.mongo[self.dbName].soccer.insert(self.items)

	def testInterval(self):
		"""It should return only the items matching the timeframe."""
		response = self.server.get('/items/?subreddit=soccer&from=1&to=8')

		self.assertEqual(json.loads(response.data)['data'], self.items[0:1], "Wrong items returned.")

	def testDataOrdering(self):
		"""It should return the items in reverse chronological order."""
		response = self.server.get('/items/?subreddit=soccer&from=1&to=10')

		self.assertEqual(json.loads(response.data)['data'], self.items[::-1], "Wrong item ordering.")

	def testKeyword(self):
		"""It should return only the items matching the keyword."""
		response = self.server.get('/items/?subreddit=soccer&from=1&to=10&keyword=bar')

		self.assertEqual(json.loads(response.data)['data'], self.items[-1:], "Wrong items returned.")

	def testMissingParameter(self):
		"""A missing parameter should yield 404 response."""
		response = self.server.get('/items/?subreddit=soccer&from=1')

		self.assertEqual(response._status_code, 404, "Wrong status response.")

	def testNotFound(self):
		"""Incorrect route should yield 404 response."""
		response = self.server.get('/test/')

		self.assertEqual(response._status_code, 404, "Wrong status response.")

	def tearDown(self):
		"""Cleanup"""
		self.mongo.drop_database(self.dbName)

def test_run():
	unittest.main(exit = False)

if __name__ == '__main__':
	test_run()