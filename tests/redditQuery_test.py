import mock
import src.redditQuery as redditquery
import unittest

class RedditQueryTest(unittest.TestCase):
	def setUp(self):
		"""Set up mock reddit client."""
		self.rq = redditquery.RedditQuery('tests/test_config.json')

	def testWorkerCount(self):
		"""It should spawn numThreads workers."""
		self.rq.pollingWorker = mock.MagicMock()
		self.rq.startPolling()

		assert(self.rq.pollingWorker.call_count == 4)

def test_run():
	unittest.main(exit = False)

if __name__ == '__main__':
	test_run()