from flask import Flask
from flask.globals import request
from elasticsearch import Elasticsearch
import json

app = Flask(__name__)

es = Elasticsearch(
    "http://node-2.hska.io:9200/"
)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

# send query via: .../search?query=<insert query here>
@app.route("/search")
def search():
    '''
    q = request.args.get('query')
    q = json.loads(q)
    res = es.search(index="beer_recipes", query=q)
    '''
    print(request.data)
    return "done"


app.run(host = "0.0.0.0")

# wie viele verschiedenen brew methods