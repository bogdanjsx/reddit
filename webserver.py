import argparse
import database
import flask
import json

app = flask.Flask(__name__)

@app.route('/items/')
def query():
	"""Query the database for the requested subreddit."""
	subreddit = flask.request.args.get('subreddit')
	startTime = int(flask.request.args.get('from'))
	endTime = int(flask.request.args.get('to'))
	keyword = flask.request.args.get('keyword')

	if subreddit == None or startTime == None or endTime == None:
		return 'Error: please supply all parameters'

	query = {'timestamp': {'$gte': startTime, '$lt': endTime}}
	if keyword != None:
		query['$text'] = {'$search': keyword}

	sort = [('timestamp', database.DESCENDING)]

	return flask.jsonify({'data' : list(db.queryItems(subreddit, query, sort))})

@app.errorhandler(404)
def pageNotFound():
	"""Standard 404 handler"""
	return 'There\'s nothing here, please access /items/ to get your data.'

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('--config_file', type = str, default = 'config.json', help = 'Config')
	args = parser.parse_args()

	with open(args.config_file) as configFile:
		configData = json.load(configFile)

	db = database.Database(configData['databaseName'], configData['subreddits'])
	app.run()