from elasticsearch import Elasticsearch, helpers
from bs4 import BeautifulSoup
import os
import networkx as nx
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
import jieba
import csv

#初始化es客户端
es=Elasticsearch(
    hosts=["http://localhost:9200"],
    http_auth=('elastic', '123456')
)

#创建索引
index_name = 'html_index'
index_body = {
    "settings": {
        "analysis": {
            "analyzer": {
                "ik_analyzer": {
                    "type": "custom",
                    "tokenizer": "ik_max_word",
                    "filter": ["lowercase"]
                }
            }
        }
    },
    "mappings": {
        "properties": {
            "title": {"type": "text", "analyzer": "ik_analyzer"},
            "url": {"type": "keyword"},
            "anchor_text": {"type": "text", "analyzer": "ik_analyzer"},
            "content": {"type": "text", "analyzer": "ik_analyzer"}
        }
    }
}

#执行搜索
def conduct_query(query_word,es=es,index_name=index_name,query_size=None):
    query={}
    if query_size is not None:
        query={
            "query":{
                "multi_match":{
                    "query":query_word,
                    "fields":['title','anchor_text','context']
                }
            },
            'size':query_size
        }
    else:
        query={
            "query":{
                "multi_match":{
                    "query":query_word,
                    "fields":['title','anchor_text','context']
                }
            },
        }
    
    respond=es.search(index=index_name,body=query)
    query_cnt=0
    for hit in respond['hits']['hits']:
        query_cnt+=1
        
        title=hit['_source']['title']
        content=hit['_source']['content']
        url=hit['_source']['url']
        
        #去除html标签
        soup=BeautifulSoup(content,'html')
        text_content=soup.get_text()
        cleaned_content=' '.join(text_content.split()) #去除所有空字符
        print(f"Title:{title}")
        print(f'url: {url}')
        print(f'content: {cleaned_content[:250]}...')
        print("-"*50)
        
        if query_cnt>10:
            break
        
    return len(respond['hits']['hits'])
        
if __name__=="__main__":
    while True:
        print("input your query, QUIT to quit.")
        query_word=input()
        if query_word=="QUIT":        
            break
        else:
            query_num=conduct_query(query_word=query_word,query_size=10000)
            print(f'Find {query_num} results.')