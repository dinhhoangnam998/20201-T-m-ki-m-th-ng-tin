from elasticsearch import Elasticsearch, ConflictError, NotFoundError
from datetime import datetime

from config.config import ElasticSearchConfig

es = Elasticsearch(
    [{'host': ElasticSearchConfig.ELASTICSEARCH_IP_ADDRESS, 'port': ElasticSearchConfig.ELASTICSEARCH_PORT}])


def save_data(content, link):
    img = {
        'content': content,
        'link': link,
        'created': datetime.now()
    }
    try:
        res = es.index(index=ElasticSearchConfig.INDEX_COVID, body=img)
        print("data saved")
        return 1
    except:
        print("error")
        return 0


def get_data(size=10, start=0):
    query = {
        "size": size,  # default 10
        "from": start,  # default 0
        "sort": {
            "created": {"order": "desc"}
        },
        "query": {
            "match_all": {},
        }
    }
    try:
        res = es.search(index=ElasticSearchConfig.INDEX_COVID, body=query)
        return res['hits']['hits']
    # if not found res will not contain ['hits']['hits'][0]['_source']
    except IndexError:
        print("have no image")


def enable_fielddata(field):
    body = {
        "properties": {
            field: {
                "type": "text",
                "fielddata": True
            }
        }
    }

    es.indices.put_mapping(index=ElasticSearchConfig.INDEX_IMAGE, body=body)


# enable_fielddata("created")
