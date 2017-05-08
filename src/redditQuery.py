import argparse
import database
import json
import praw
import threading
import time

class RedditQuery(object):
	"""Calls the Reddit API periodically and stores results in the database."""
	def __init__(self, configFile = ''):
		# Initialize reddit instance and db using config file
		with open(configFile) as configFile:
			configData = json.load(configFile)

		self.reddit = praw.Reddit(
			client_id = configData['redditCredentials']['clientId'],
			client_secret = configData['redditCredentials']['clientSecret'],
			user_agent = configData['redditCredentials']['userAgent']
		)

		now = time.time()
		self.subreddits = {
			name : {
				'updated': now,
				'instance': self.reddit.subreddit(name)
			} for name in configData['subreddits']
		}

		self.numThreads = configData['numThreads']
		self.commentLimit = configData['commentLimit']
		self.pollingInterval = configData['pollingInterval']
		self.verbose = configData['verbose']
		self.db = database.Database(configData['databaseName'], configData['subreddits'])

	def startPolling(self):
		"""Starts calling the Reddit API to fetch submissions and comments."""

		# If only one thread is needed, start polling from the master thread.
		if self.numThreads == 1:
			self.pollingWorker(self.subreddits)
		else:
			threads = []

			# Convert dict to list to pass each thread every numThread-th item.
			subreddits = [(name, sub) for name, sub in self.subreddits.items()]

			# Start numThread workers, each with his own subreddits.
			for threadNo in range(self.numThreads):
				subredditSlice = {
					subreddits[idx][0]: subreddits[idx][1]
					for idx in range(len(subreddits))
					if idx % self.numThreads == threadNo
				}
				thread = threading.Thread(
					target = self.pollingWorker,
					args = (subredditSlice, str(threadNo))
				)
				threads.append(thread)
				thread.start()

			# This will never get called if polling indefinitely.
			for idx in range(self.numThreads):
				threads[idx].join()

	def pollingWorker(self, subreddits, name = 'Master'):
		"""Function for the worker threads, should never be called from outside the class."""
		while(True):
			time.sleep(self.pollingInterval)
			for subreddit in subreddits:
				data = subreddits[subreddit]

				# Fetch and format all submissions newer than the stored timestamp.
				submissions = [self.formatSubmission(submission, subreddit)
					for submission in data['instance'].submissions(start = data['updated'])]

				# Fetch and format last commentLimit
				comments = [self.formatComment(comment, subreddit)
					for comment in data['instance'].comments(limit = self.commentLimit)
					if comment.created_utc > data['updated']]

				data['updated'] = time.time()

				submisssionsInserted = len(submissions)
				commentsInserted = len(comments)

				self.db.insertItems(subreddit, submissions + comments)

				if self.verbose:
					print ('[Thread %s]: Inserted %d submissions and %d comments into %s.' %
						(name, submisssionsInserted, commentsInserted, subreddit))

	def formatComment(self, comment, subreddit):
		"""Formats a comment into its final database form."""
		return {
			'_id': comment.id,
			'author': comment.author.name,
			'score': comment.score,
			'subreddit': subreddit,
			'text': comment.body,
			'timestamp': comment.created_utc,
			'type': 'comment',
		}

	def formatSubmission(self, submission, subreddit):
		"""Formats a submission into its final database form."""
		return {
			'_id': submission.id,
			'author': submission.author.name,
			'score': submission.score,
			'subreddit': subreddit,
			# 'text': submission.selftext,
			'title': submission.title,
			'timestamp': submission.created_utc,
			'type': 'submission',
			'url': submission.selftext_url,
		}

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('--config_file', type = str, default = 'config.json', help='Config')
	args = parser.parse_args()

	redditQuery = RedditQuery(args.config_file)
	redditQuery.startPolling()