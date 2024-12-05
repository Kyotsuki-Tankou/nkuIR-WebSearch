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

def gen_query(query_word_term,query_word_phrase,fields):#生成基础查询
    #精准匹配，也就是"南开大学"-X->"南开是大学"
    must_clauses=[]
    for query_word in query_word_term:
        must_clauses.append(
            {
            "bool": {
                "should": [
                    {"match_phrase": {field: query_word}} for field in fields
                ],
                "minimum_should_match": 1
            }
        }
        )
    #模糊匹配，也就是"南开大学"->"南开是大学"且"南开大学"->"南"
    for query_word in query_word_phrase:
        # should_clauses.append(
        must_clauses.append(
        {
            "bool": {
                "should": [
                    {"match": {field: query_word}} for field in fields
                ],
                "minimum_should_match": 1
            }
        }
        )
        
    query={
        "query":{
            "bool":{
                "must":must_clauses,
            }
        }
    }
    return query
    
#执行搜索
def conduct_basic_query(query_word_term=[],query_word_phrase=[],
                        es=es,index_name=index_name,fields=['title','anchor','content'],
                        query_size=None):
    query=gen_query(query_word_term=query_word_term,query_word_phrase=query_word_phrase,fields=fields)

    response=es.search(index=index_name,body=query,scroll='2m',size=2000)#使用滚动方式进行获取
    
    scroll_id=response['_scroll_id']
    results=response['hits']['hits']
    query_len=len(results)
    query_cnt=0
    for hit in results:
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
    while len(results):
        if query_len>=query_size:
            break
        response=es.scroll(scroll_id=scroll_id,scroll='2m')
        scroll_id=response['_scroll_id']
        results=response['hits']['hits']
        query_len+=len(results)
        
    return query_len

if __name__=="__main__":
    while True:
        print("Input the precise word match (split with '^' without quote):")
        query_word_term=[]
        query_word_phrase=[]
        
        query_word=input()
        query_word_term=list(set(query_word.split('^')))
        query_word_term=[s for s in query_word_term if s.strip()]
        if query_word=='^':
            query_word_term=[]
            
        print("Input the ambiguity word match (split with '^' without quote with not necessarility):")
        query_word=input()
        query_word_phrase=list(set(query_word.split('^')))
        query_word_phrase=[s for s in query_word_phrase if s.strip()]
        if query_word=='^':
            query_word_phrase=[]
        
        # print(query_word_term)
        # print(query_word_phrase)
        # print(len(query_word_term),len(query_word_phrase))

        query_num=conduct_basic_query(query_word_term=query_word_term,query_word_phrase=query_word_phrase,query_size=131072)
        
        print(f'Find {query_num} results.')
        print("QUIT to quit (not case sensitive).")
        quit_word=input()
        if quit_word.lower()=="quit":        
            break