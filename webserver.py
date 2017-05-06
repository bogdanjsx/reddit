from flask import Flask, request, jsonify
from argparse import ArgumentParser
import database
import pymongo
import json
from pprint import pprint

app = Flask(__name__)

@app.route("/items/")
def query():
	subreddit = request.args.get('subreddit')
	startTime = int(request.args.get('from'))
	endTime = int(request.args.get('to'))
	keyword = request.args.get('keyword')

	if subreddit == None or startTime == None or endTime == None:
		return "Error: please supply all parameters"

	query = {'timestamp': {'$gte': startTime, '$lt': endTime}}
	if keyword != None:
		query['$text'] = {'$search': keyword}

	sort = [('timestamp', pymongo.DESCENDING)]

	# pprint(db.queryItems(subreddit, query, sort).explain())

	return jsonify({"data" : list(db.queryItems(subreddit, query, sort))})

@app.errorhandler(404)
def page_not_found():
	return "There's nothing here, please access /items/ to get your data."

if __name__ == "__main__":
	parser = ArgumentParser()
	parser.add_argument("--config_file", type = str, default = 'config.json', help="Config")
	args = parser.parse_args()

	with open(args.config_file) as configFile:
		configData = json.load(configFile)

	db = database.Database(configData['databaseName'], configData['subreddits'])
	app.run()