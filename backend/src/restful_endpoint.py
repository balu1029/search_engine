from flask import Flask
from elasticsearch import Elasticsearch

app = Flask(__name__)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"


app.run()
