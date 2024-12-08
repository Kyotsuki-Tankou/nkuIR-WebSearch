#用来将pages下的页面根据pdf2url映射表导入es中
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
            "content": {"type": "text", "analyzer": "ik_analyzer"},
            "pagerank": {"type": "float"}
        }
    }
}

if not es.indices.exists(index=index_name):
    es.indices.create(index=index_name, body=index_body)

# 读取pdf2url.csv文件
pdf2url={}
with open('./pdf/pdf2url.csv','r',encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        pdf2url[row['title']]=row['url']

# 读取pages文件夹下的HTML文件
cnt=0
batch_size=1000
actions=[]

#pagerank
graph=nx.DiGraph()

for filename in os.listdir('./pdf/pdfs'):
    if filename.endswith('.pdf'):
        title = os.path.splitext(filename)[0]
        # print(title)
        url = pdf2url.get(title+'.pdf')
        if url:
            # print(filename)
            with open(os.path.join('./pdf/pdfs', filename),'r',encoding='utf-8') as file:
                cnt+=1
                anchor_texts=filename
                action={
                    "_index":index_name,
                    "_source":{
                        "title":title,
                        "url":url,
                        "anchor_text":' '.join(anchor_texts),
                        "content":filename
                    }
                }
                actions.append(action)
                if cnt%batch_size==0:
                    print(f"cnt: {cnt}")
                    helpers.bulk(es,actions)
                    actions=[]

#pagerank，为了防止pagerank过分影响结果，线性映射到[1,2]区间内
# pagerank=nx.pagerank(graph)
# min_pr=min(pagerank.values())
# max_pr=max(pagerank.values())
# mapped_pagerank={url:1+(pr-min_pr)/(max_pr-min_pr) for url,pr in pagerank.items()}

for action in actions:
    url=action["_source"]["url"]
        
if __name__=="__main__":
    # 批量索引数据到Elasticsearch
    if actions:
        helpers.bulk(es, actions)
    print("Indexing completed.")