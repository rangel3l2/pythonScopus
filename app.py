# cSpell:disable
try:
    import flask
    import requests
except ImportError:
    raise ImportError("error when importing flask and requests")

from flask import Flask, request, Response, send_file, redirect, render_template
import requests
import json
import csv
import os


app = Flask(__name__)
BASEURL = "https://api.elsevier.com/content/search/scopus"
TYPE = "application/json"
HEADERS = lambda apikey: {"Accept": TYPE, "X-ELS-APIKey": apikey}
FIELD = 'title,authors,publicationName,coverDate,authkeywords,volume'  
DATE = "2018-2022"
PATH = "static/results.csv"
KEYWORDS = []
APIKEY = 'fbb475267a209868a30c9f9806956e05'
if not os.path.exists("static"):
    os.mkdir("static")
if os.path.exists(PATH):
    os.remove(PATH)


def get_response(data: dict = None, code: int = 200) -> Response:
    HEADERS = {"Access-Control-Allow-Origin": "*", "Access-Control-Allow-Credentials": True, "Content-Type": TYPE}
    if data is None:
        return Response(None, code, HEADERS, mimetype=TYPE)
    return Response(json.dumps(data, indent=2), code, HEADERS, mimetype=TYPE)

@app.route("/", methods=['POST','GET'])
def home(): 
    if request.method == 'GET':
        
        return render_template('scopus.html')
 
 
     


@app.route("/scopus-api",methods=['POST','GET'])
def scopus_api():
    
    if request.method == "GET":

        
        
        # keywords = request.args.get("keywords")
        # if keywords is None or len(keywords) == 0:
        #     return get_response({"message": "keywords not found"}, 400)

        # keywords = keywords.split(",")
        # keywords = [keyword for keyword in keywords if (len(keyword) > 1) and (not keyword.isspace())]
        # QUERY_VALUES = " AND ".join(keywords)

        url = f"{BASEURL}?query=TITLE-ABS-KEY(mouse OR rat AND rodent)&{APIKEY}&field={FIELD}&{DATE}"
        requisition = requests.get(url, headers=HEADERS(APIKEY))
        if len(requisition.text) == 0:
            return get_response({"message": "error in returning response"}, 200)

        response = json.loads(requisition.text.encode("utf-8"))
        total_results = response["search-results"]["opensearch:totalResults"]
        if int(total_results) == 0:
            return get_response({"message": "none articles has been found"}, 200)

        def map_result(params: dict) -> dict:
            return {
                "Title": params.get("dc:title"),
                "Publication Name": params.get("prism:publicationName"),
                "Date": params.get("prism:coverDate"),
                "Volume": params.get("prism:volume"),
                "URL": params.get("prism:url"),
            }

        response_results: list = response["search-results"]["entry"]
        results_dicts = [map_result(result) for result in response_results]
        # print(json.dumps({"Results": results_dicts}, sort_keys=True, indent=2, separators=(",", ": ")), "\n")

        with open(PATH, "w", newline="") as file:
            writer = csv.writer(file, delimiter=",")
            writer.writerow(["Title", "Publication Name", "Date", "Volume", "URL"])
            for result in results_dicts:
                writer.writerow(result.values())

        return send_file(PATH, "CSV", True, "results.csv")



app.run(debug=True)