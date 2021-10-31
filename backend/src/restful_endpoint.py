from flask import Flask
from flask.globals import request
from elasticsearch import Elasticsearch
import json
from flask_cors import CORS, cross_origin
from elasticsearch_dsl import Search, Q, A
from elasticsearch_dsl.query import MultiMatch
from difflib import SequenceMatcher

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

base_url = "https://www.brewersfriend.com"
num_autocomplete = 7
num_results = 20

es = Elasticsearch(
    "http://node-2.hska.io:9200/"
)


@app.route("/")
@cross_origin()
def hello_world():
    return "Supporting /search[POST], /autocomplete[GET], /brew[GET]"


@app.route("/search",methods = ['POST'])
@cross_origin()
def search():
    
    req = json.loads(request.data)

    s = Search(using = es, index = "beer_recipes")
    query = MultiMatch(query = req["query"], fields = ["Name", "Style"], fuzziness = 1)#Q("match", Name = req["query"]) | Q("match", Style = req["query"])
    s = s.query(query)


    # exception handling for empty requests and filtering 
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
    
    # implementation of the load more function
    try:
        start = int(request.args.get("offset"))
    except:
        start = 0
    if(s.count() > start + num_results):
        s = s[start:start+num_results]
    else:
        s = s[start:]

    # find out how many of each brew methods are in the results
    aggregation = A("terms", field = "BrewMethod")
    s.aggs.bucket("dist_brewmethods_per_result", aggregation)

    es_res = s.execute()

    res = {}
    hits = []
    for hit in es_res:  
        try:
            response = {}
            response["name"] = hit.Name
            response["url"] = base_url + hit.URL
            response["abv"] = hit.ABV
            response["brewMethod"] = hit.BrewMethod
            response["style"] = hit.Style
    
            hits.append(response)
        except:
            continue
    res["hits"] = hits

    aggregs = {}
    for elem in es_res["aggregations"]["dist_brewmethods_per_result"]["buckets"]:
        aggregs[elem["key"].replace(" ", "")] = elem["doc_count"]

    aggregs["num_hits"] = s.count()
    res["aggs"] = aggregs   
    
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

    # high fuzziness because of typos in search bar
    s = s.query(MultiMatch(query = q, fields = ["Name", "Style"], fuzziness = 5))
    if(s.count() > num_autocomplete):
        s = s[0:num_autocomplete]
    else:
        s = s[:]
    es_res = s.execute()

    methods = []
    res = {}
    count = 0
    for hit in es_res:

        #check which of the two fields match better
        if SequenceMatcher(None, str(q), str(hit["Style"])).ratio() > \
           SequenceMatcher(None, str(hit["Name"]), str(q)).ratio():
           val = hit["Style"]
        else:
            val = hit["Name"]

        # don't autocomplete the same word
        if str(val).lower() == str(q).lower():
            continue
        
        #max num of autocompletion suggestions
        if count < num_autocomplete:
            if val not in methods:
                methods.append(val)
                count = count + 1
        else:
            break
        
    res["results"] = methods
    return json.dumps(res)

app.run(host = "0.0.0.0")
