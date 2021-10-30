from flask import Flask
from flask.globals import request
from elasticsearch import Elasticsearch
import json
from flask_cors import CORS, cross_origin
from elasticsearch_dsl import Search, Q, A
from elasticsearch_dsl.query import Match

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
base_url = "https://www.brewersfriend.com"

es = Elasticsearch(
    "http://node-2.hska.io:9200/"
)


@app.route("/")
def hello_world():
    return "Supporting /search[POST], /autocomplete[GET], /brew[GET]"


@app.route("/search",methods = ['POST'])
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

    s = Search(using = es, index = "beer_recipes")
    query = Q("match", Name = req["query"]) | Q("match", Style = req["query"])
    s = s.query(query)

    if(s.count() > 20):
        s = s[0:20]
    else:
        s = s[:]

    try:
        if req["extraOptions"]["minABV"] == "":
            req["extraOptions"]["minABV"] = 0
    except:
        req["extraOptions"]["minABV"] = 0  
    try:
        if req["extraOptions"]["maxABV"] == "":
            req["extraOptions"]["maxABV"] = 100
    except:
        req["extraOptions"]["maxABV"] = 100
    try:
        if req["extraOptions"]["brewMethod"] != "":
            s = s.filter("term", **{"BrewMethod" : req["extraOptions"]["brewMethod"]})
    except:
        req["extraOptions"]["brewMethod"] = ""

    s = s.filter("range", **{"ABV": {"from": req["extraOptions"]["minABV"], "to": req["extraOptions"]["maxABV"]}})
    
    es_res = s.execute()

    for hit in es_res:  
        try:
            response = {}
            response["name"] = hit.Name
            response["url"] = base_url + hit.URL
            response["abv"] = hit.ABV
            response["brewMethod"] = hit.BrewMethod
            response["style"] = hit.Style

            res.append(response)
        except:
            continue
        
    return json.dumps(res)





@app.route("/brew",methods = ['GET'])
@cross_origin()
def brew():
    s = Search(using = es, index = "beer_recipes")
    aggregation = A("terms", field = "BrewMethod")
    s.aggs.bucket("dist_brewmethods", aggregation)
    es_res = s.execute()

    methods = []
    res = {}

    methods.append("")
    for elem in es_res["aggregations"]["dist_brewmethods"]["buckets"]:
        methods.append(elem["key"])
    res["results"] = methods
    return json.dumps(res)

@app.route("/autocomplete",methods = ['GET'])
@cross_origin()
def autocomplete():

    q = request.args.get("query")
    s = Search(using = es, index = "beer_recipes")

    #query = Q(**{"fuzzy":{ "Name" : {"value": q, "fuzziness" : 2}}})

    s = s.query(Match(Name={"query": q, "fuzziness":8}))
    es_res = s.execute()

    methods = []
    res = {}
    count = 0
    for hit in es_res:
        if str(q).lower() in str(hit["Name"]).lower():
            val = hit["Name"]
        elif str(q).lower() in str(hit["Style"]).lower():
            val = hit["Style"]
        else:
            continue

        if str(val) == str(q):
            continue
        
        if count < 7:
            if val not in methods:
                methods.append(val)
                count = count + 1
        else:
            break
        
    res["results"] = methods
    return json.dumps(res)

app.run(host = "0.0.0.0")
