import time
import praw
import database
import json
from argparse import ArgumentParser
from pprint import pprint

COMMENT_LIMIT = 100
SECONDS_BETWEEN_REQUESTS = 1

class RedditQuery(object):
	"""docstring for RedditQuery"""
	def __init__(self, configFile = ''):

		# Initialize reddit instance and db using config file
		with open(configFile) as configFile:
			configData = json.load(configFile)

		self.reddit = praw.Reddit(
			client_id = configData['redditCredentials']['clientId'],
			client_secret = configData['redditCredentials']['clientSecret'],
			user_agent = configData['redditCredentials']['userAgent'])

		now = time.time()
		self.subreddits = {
			name : {
				'updated': now,
				'instance': self.reddit.subreddit(name)
			} for name in configData['subreddits']
		}

		self.db = database.Database(configData['databaseName'], configData['subreddits'])

	def startPolling(self):
		self.db.clearDatabase()

		while(True):
			time.sleep(SECONDS_BETWEEN_REQUESTS)

			for subreddit in self.subreddits:
				data = self.subreddits[subreddit]

				# Fetch and format all submissions newer than the stored timestamp
				submissions = [self.formatSubmission(submission, subreddit)
					for submission in data['instance'].submissions(start = data['updated'])]

				print("inserting submissions")
				print(len(submissions))
				self.db.insertItems(subreddit, submissions)

				comments = [self.formatComment(comment, subreddit)
					for comment in data['instance'].comments(limit = COMMENT_LIMIT)
					if comment.created_utc > data['updated']]

				print("inserting comments")
				print(len(comments))
				self.db.insertItems(subreddit, comments)

				data['updated'] = time.time()


	def formatComment(self, comment, subreddit):
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
		return {
			'_id': submission.id,
			'author': submission.author.name,
			'score': submission.score,
			'subreddit': subreddit,
			'text': submission.selftext,
			'title': submission.title,
			'timestamp': submission.created_utc,
			'type': 'submission',
			'url': submission.url,
		}

if __name__ == '__main__':
	parser = ArgumentParser()
	parser.add_argument("--config_file", type = str, default = 'config.json', help="Config")
	args = parser.parse_args()

	rq = RedditQuery(args.config_file)
	rq.startPolling()