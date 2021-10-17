from flask import Flask
from elasticsearch import Elasticsearch

app = Flask(__name__)

es = Elasticsearch(
    "http://node-2.hska.io:9200/"
)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"



res = es.search(index="beer_recipes", query={"range":{"ABV":{"gte":10}}})
print(res["hits"]["hits"][-1]["_source"]["ABV"])
#app.run()
