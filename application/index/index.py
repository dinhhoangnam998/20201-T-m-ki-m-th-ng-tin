'''
for api of app
'''
import json

from flask import Blueprint, request, render_template, url_for, redirect
from flask import jsonify

from db_services.neo4j_services import match_neo4jformat, update_graph
from knowledge_graph.knowledge_graph_interact import verifyInfo

index_api = Blueprint('index_api', __name__,
                      template_folder='../../frontend/public',
                      static_folder='../../frontend/public',
                      static_url_path='/static_img'
                      )


@index_api.route("/verify", methods=['GET', 'POST'])
def verify():
    content = request.form['content']
    return verifyInfo(content)


@index_api.route("/visualization", methods=['GET', 'POST'])
def visualization():
    # query = "MATCH p=()-[r:ACTED_IN]->() RETURN p LIMIT 25"
    data = match_neo4jformat()

    return data

@index_api.route("/updateGraph", methods=['GET', 'POST'])
def updateGraph():
    content = request.json['content']
    time= request.json['time']
    link = request.json['link']
    update_graph(content, time, link)

    return "success"

