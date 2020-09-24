"""
Module process data with pyspark
"""

import json
import pyspark as ps
from pyspark.streaming import StreamingContext
from db_services.neo4j_services import update_graph

conf = ps.SparkConf().setMaster("local[*]").setAppName("StreamingCovid19")
sc = ps.SparkContext('local[*]', '', conf=conf)
ssc = StreamingContext(sc, 60)
# Create a DStream that will connect to hostname:port, like localhost:9999
# lines = ssc.socketTextStream("localhost", 9999)

lines = ssc.textFileStream("E:/HUST/bigdata/covid_verification/dataprocessing/data")
# lines = ssc.textFileStream("C:/Users/HoangNam/Documents/code/xproject/covid_verification/dataprocessing/streaming/data")


def extractER(line):
    article = json.loads(line)
    return (article['content'], article['time'], article['link'])


def batch_update_graph(triples):
    for triple in triples:
        update_graph(triple[0], triple[1], triple[2])


words = lines.map(extractER)
words.foreachRDD(lambda rdd: rdd.foreachPartition(batch_update_graph))
words.pprint()
ssc.start() 
ssc.awaitTermination()  
