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

index_settings = {
    "settings": {
        "analysis": {
            "analyzer": {
                "default": {
                    "type": "custom",
                    "tokenizer": "ik_max_word",
                    "filter": ["lowercase"]
                }
            }
        }
    },
    "mappings": {
        "properties": {
            "title": {
                "type": "text",
                "fields": {
                    "keyword": {
                        "type": "keyword"
                    }
                }
            },
            "content": {
                "type": "text",
                "fields": {
                    "keyword": {
                        "type": "keyword"
                    }
                }
            },
            "anchor": {
                "type": "text"
            },
            "url": {
                "type": "keyword"
            }
        }
    }
}

# 创建索引
es.indices.create(index=index_name, body=index_settings)