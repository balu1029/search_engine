from flask import Flask
from flask.globals import request
from elasticsearch import Elasticsearch
import json
from flask_cors import CORS, cross_origin
from elasticsearch_dsl import Search, Q
from elasticsearch_dsl.query import Match

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

es = Elasticsearch(
    "http://node-2.hska.io:9200/"
)


@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"


@app.route("/search",methods = ['POST', 'GET'])
@cross_origin()
def search():
    '''
    q = request.args.get('query')
    q = json.loads(q)
    res = es.search(index="beer_recipes", query=q)
    '''
    print(request.data)
    res = []
    req = json.loads(request.data)

    s = Search(using = es)
    query = Q("match", Name = req["query"]) | Q("match", Style = req["query"])
    s = s.query(query)

    try:
        if req["minABV"] == "":
            req["minABV"] = 0
    except:
        req["minABV"] = 0  
    try:
        if req["maxABV"] == "":
            req["maxABV"] = 100
    except:
        req["maxABV"] = 100
    try:
        if req["brewMethod"] != "":
            s = s.filter("term", **{"BrewMethod" : req["brewMethod"]})
    except:
        req["brewMethod"] = ""

    s = s.filter("range", **{"ABV": {"from": req["minABV"], "to": req["maxABV"]}})
    
    es_res = s.execute()

    for hit in es_res:  
        try:
            response = {}
            response["name"] = hit.Name
            response["url"] = hit.URL
            response["abv"] = hit.ABV
            response["brewMethod"] = hit.BrewMethod
            response["style"] = hit.Style

            res.append(response)
        except:
            continue
        
    return json.dumps(res)

@app.route("/auto",methods = ['GET'])
@cross_origin()
def auto():


app.run(host = "0.0.0.0")

# wie viele verschiedenen brew methods