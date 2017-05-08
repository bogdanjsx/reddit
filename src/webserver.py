import argparse
import database
import flask
import json

app = flask.Flask(__name__)
db = None

def initDatabase(configData, createIndexes):
	global db
	db = database.Database(configData['databaseName'], configData['subreddits'], createIndexes)

@app.route('/items/')
def query():
	"""Query the database for the requested subreddit."""
	subreddit = flask.request.args.get('subreddit')
	startTime = flask.request.args.get('from')
	endTime = flask.request.args.get('to')
	keyword = flask.request.args.get('keyword')

	if subreddit == None or startTime == None or endTime == None:
		return pageNotFound(True)

	startTime = int(startTime)
	endTime = int(endTime)

	query = {'timestamp': {'$gte': startTime, '$lt': endTime}}
	if keyword != None:
		query['$text'] = {'$search': keyword}

	sort = [('timestamp', database.DESCENDING)]

	response = flask.jsonify({
		'data' : list(db.queryItems(subreddit, query, sort)),
		'status': 200
	})
	response.status_code = 200

	return response

@app.errorhandler(404)
def pageNotFound(_):
	"""Standard 404 handler"""
	response = flask.jsonify({
		'message': 'There\'s nothing here, please access /items/ to get your data.',
		'status': 404,
	})
	response.status_code = 404

	return response

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('--config_file', type = str, default = 'config.json', help = 'Config')
	args = parser.parse_args()

	with open(args.config_file) as configFile:
		configData = json.load(configFile)

	initDatabase(configData, False)
	app.run(threaded = True, host = '0.0.0.0')