import os
import cPickle as pickle
import json
import re

from textblob import TextBlob
from textblob.sentiments import NaiveBayesAnalyzer
from pymongo import MongoClient

from pyspark import SparkContext, SparkConf
from pyspark.streaming import StreamingContext

appName = "Tweet Monitor"
master = "local[*]"

conf = SparkConf().setAppName(appName).setMaster(master)
sc = SparkContext(conf=conf)
ssc = StreamingContext(sc, 5)

flag_words_file = "/root/twitter-spark/data/filter_words.txt"
happy_words_file = "/root/twitter-spark/data/happy_words.txt"
flagged_words = []
happy_words = []

def read_words():
    global flagged_words
    global happy_words
    f = open(flag_words_file,'r')
    flagged_words = f.read().split()
    f.close()
    f = open(happy_words_file,'r')
    happy_words = f.read().split()
    f.close()

def stream():
    lines = ssc.socketTextStream("localhost", 9999)
    lines_unpickled = lines.map(lambda x: json.loads(x))
    filteredNeg = lines_unpickled.flatMap(analyze)
    filteredPos = lines_unpickled.flatMap(analyze2)

    inserted = filteredNeg.mapPartitions(mapper)
    inserted2 = filteredPos.mapPartitions(mapper2)

    inserted.pprint()
    inserted2.pprint()

def mapper(iter):
    db = MongoClient('mongodb://localhost:27017/').t4.tweets
    db1 = MongoClient('mongodb://localhost:27017/').t4.neg
    for val in iter:
        yield db.insert(val)
        yield db1.insert(val)
def mapper2(iter):
    db = MongoClient('mongodb://localhost:27017/').t4.tweets
    db1 = MongoClient('mongodb://localhost:27017/').t4.pos
    for val in iter:
        yield db.insert(val)
        yield db1.insert(val)

def analyze(data):
    text = data['text'].lower()

    sentiment = TextBlob(text, analyzer=NaiveBayesAnalyzer()).sentiment.classification
    if sentiment=="neg":
        return [data]
    else:
        return []

def analyze2(data):
    text = data['text'].lower()
    sentiment = TextBlob(text, analyzer=NaiveBayesAnalyzer()).sentiment.classification
    if sentiment=="pos":
        return [data]
    else:
        return []

def flag_by_keyword(data):
    text = data['text'].lower()
    for x in flagged_words:
        if x in text:
            flag = True
            for y in happy_words:
                if y in text:
                    flag = False
            if flag:
                print x,text
                return [data]
    return []

def main():
    read_words()
    stream()
    ssc.start()
    ssc.awaitTermination()

if __name__=="__main__":
    main()
