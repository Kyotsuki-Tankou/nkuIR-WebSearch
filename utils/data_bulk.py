#用来将pages下的页面根据title2url映射表导入es中
from elasticsearch import Elasticsearch, helpers
from bs4 import BeautifulSoup
import os
import networkx as nx
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
import jieba
import csv

# 初始化Elasticsearch客户端
es = Elasticsearch(
    hosts=["http://localhost:9200"],
    http_auth=('elastic', '123456')
)


# # 创建索引和映射
index_name='html_index'
index_body={
    "settings":{
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
    "mappings":{
        "properties": {
            "title": {"type": "text", "analyzer": "ik_analyzer"},
            "url": {"type": "keyword"},
            "anchor_text": {"type": "text", "analyzer": "ik_analyzer"},
            "content": {"type": "text", "analyzer": "ik_analyzer"}
        }
    }
}

if not es.indices.exists(index=index_name):
    es.indices.create(index=index_name, body=index_body)

# 读取title2url.csv文件
title2url={}
with open('title2url.csv','r',encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        title2url[row['title']]=row['url']

# 读取pages文件夹下的HTML文件
cnt=0
batch_size=1000
actions=[]

for filename in os.listdir('pages'):
    if filename.endswith('.html'):
        title = os.path.splitext(filename)[0]
        url = title2url.get(title)
        if url:
            with open(os.path.join('pages', filename),'r',encoding='utf-8') as file:
                cnt+=1
                soup=BeautifulSoup(file,'html.parser')
                content=soup.get_text()
                anchor_texts=[a.get_text() for a in soup.find_all('a')]

                action={
                    "_index":index_name,
                    "_source":{
                        "title":title,
                        "url":url,
                        "anchor_text":' '.join(anchor_texts),
                        "content":content
                    }
                }
                actions.append(action)
                if cnt%batch_size==0:
                    print(f"cnt: {cnt}")
                    helpers.bulk(es,actions)
                    actions=[]

if __name__=="__main__":
    # 批量索引数据到Elasticsearch
    if actions:
        helpers.bulk(es, actions)
    print("Indexing completed.")