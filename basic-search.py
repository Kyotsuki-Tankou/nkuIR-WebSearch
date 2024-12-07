from elasticsearch import Elasticsearch, helpers
from bs4 import BeautifulSoup
import os
import networkx as nx
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
from collections import Counter
import jieba
import re
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

def gen_query(query_word_term,query_word_phrase,fields,frequent_token=['程明明','青年','学者','华为']):#生成基础查询
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
    should_clauses=[]
    for query_word in query_word_phrase:
        should_clauses.append(
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
        "query": {
            "function_score": { #进行function_score查询
                "query": {#查询主体
                    "bool": {
                        "must": must_clauses,
                        "should": should_clauses
                    }
                },
                "functions": [
                    {
                        "field_value_factor": {
                            "field": "pagerank",
                            "factor": 1.0,
                            "modifier": "none",
                            "missing": 1.0
                        }
                    },
                    {
                        "script_score": {
                            "script": {#个性化加权
                                "source": """
                                    double boost = 0;
                                    for (token in params.frequent_token) {
                                        if (doc.containsKey(token)) {
                                            boost += 0.01;
                                        }
                                    }
                                    return boost;
                                """,
                                "params": {
                                    "frequent_token": frequent_token
                                }
                            }
                        }
                    }
                ],
                "boost_mode": "sum",
                "max_boost": 0.1  # 最多提高10个token的权重
            }
        },
        "highlight":{
            "fields":{
                field:{} for field in fields
            }
        }
    }
    return query
    
#执行搜索
def conduct_basic_query(query_word_term=[],query_word_phrase=[],
                        es=es,index_name=index_name,fields=['title','anchor','content'],
                        query_size=5):
    query=gen_query(query_word_term=query_word_term,query_word_phrase=query_word_phrase,
                    fields=fields)

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
        soup=BeautifulSoup(content,features="lxml")
        text_content=soup.get_text()
        cleaned_content=' '.join(text_content.split()) #去除所有空字符
        print(f"Title:{title}")
        print(f'url: {url}')
        print(f'content: {cleaned_content[:250]}...')
        
        token_counter=Counter()
        highlight_pattern=re.compile(r'<em>(.*?)</em>')#统计各个token的出现次数
        highlights=hit.get('highlight',{})
        for field,highlight in highlights.items():
            for fragment in highlight:
                tokens=highlight_pattern.findall(fragment)
                token_counter.update(tokens)
        print("Token count:")
        for token,count in token_counter.most_common():
            print(f"{token}:{count}")
            
        print("-"*50)
        if query_cnt>query_size:
            break
    while len(results):
        # if query_len>=query_size:
        #     break
        response=es.scroll(scroll_id=scroll_id,scroll='2m')
        scroll_id=response['_scroll_id']
        results=response['hits']['hits']
        query_len+=len(results)
        
    return query_len

 
#执行搜索
def conduct_regex_query(query_word_term=[],query_word_phrase=[],query_word_regex=[],
                        es=es,index_name=index_name,fields=['title','anchor','content'],
                        query_size=5):    
    # print(query_word_phrase+query_word_regex)
    
    query=gen_query(query_word_term=query_word_term,query_word_phrase=query_word_phrase+query_word_regex,
                    fields=fields)

    response=es.search(index=index_name,body=query,scroll='2m',size=2000)#使用滚动方式进行获取
    
    scroll_id=response['_scroll_id']
    results=response['hits']['hits']
    query_len=len(results)
    query_cnt=0
    regex_patterns=[re.compile(regex_word) for regex_word in query_word_regex]
    print("regex:",regex_patterns)
    for hit in results:
        title=hit['_source']['title']
        content=hit['_source']['content']
        url=hit['_source']['url']
        
        #去除html标签
        soup=BeautifulSoup(content,features="lxml")
        text_content=soup.get_text()
        
        #检查title， url和text_content中是否有匹配regex_patterns的内容，对于每个正则语句，三者有一个满足即可
        # match_miss=False
        # for pattern in regex_patterns:
        #     if not pattern.search(title) and not pattern.search(url) and not pattern.search(text_content):
        #         match_miss=True
        #         break
        match_found=any(pattern.search(title) or pattern.search(url) or pattern.search(text_content) for pattern in regex_patterns)
        if not match_found:
            continue
        query_cnt+=1
        if query_cnt>query_size:
            continue
        
        cleaned_content=' '.join(text_content.split()) #去除所有空字符
        print(f"Title:{title}")
        print(f'url: {url}')
        print(f'content: {cleaned_content[:250]}...')
        
        token_counter=Counter()
        highlight_pattern=re.compile(r'<em>(.*?)</em>')#统计各个token的出现次数
        highlights=hit.get('highlight',{})
        for field,highlight in highlights.items():
            for fragment in highlight:
                tokens=highlight_pattern.findall(fragment)
                token_counter.update(tokens)
        print("Token count:")
        for token,count in token_counter.most_common():
            print(f"{token}:{count}")
        
        print("-"*50)
        
    while len(results):
        # if query_len>=query_size:
        #     break
        # print(f"length of results is:{len(results)}")
        response=es.scroll(scroll_id=scroll_id,scroll='2m')
        scroll_id=response['_scroll_id']
        results=response['hits']['hits']
        query_len+=len(results)
        
        for hit in results:
            title=hit['_source']['title']
            content=hit['_source']['content']
            url=hit['_source']['url']
            
            #去除html标签
            soup=BeautifulSoup(content,features="lxml")
            text_content=soup.get_text()
            
            #检查title， url和text_content中是否有匹配regex_patterns的内容，对于每个正则语句，三者有一个满足即可
            # match_found=False
            # for pattern in regex_patterns:
            #     if not pattern.search(title) and not pattern.search(url) and not pattern.search(text_content):
            #         match_found=True
            #         break
                
            # if not match_found:
            #     continue
            match_found=any(pattern.search(title) or pattern.search(url) or pattern.search(text_content) for pattern in regex_patterns)
            if not match_found:
                continue
            query_cnt+=1
            if query_cnt>query_size:
                continue
            
            cleaned_content=' '.join(text_content.split()) #去除所有空字符
            print(f"Title:{title}")
            print(f'url: {url}')
            print(f'content: {cleaned_content[:250]}...')
            print("-"*50)
            
            token_counter=Counter()
            highlight_pattern=re.compile(r'<em>(.*?)</em>')#统计各个token的出现次数
            highlights=hit.get('highlight',{})
            for field,highlight in highlights.items():
                for fragment in highlight:
                    tokens=highlight_pattern.findall(fragment)
                    token_counter.update(tokens)
            print("Token count:")
            for token,count in token_counter.most_common():
                print(f"{token}:{count}")
                
    return query_cnt
    
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
        
        print("Input the RegEX match (split with '^'):")
        query_word=input()
        query_word_regex=list(set(query_word.split('^')))
        query_word_regex=[s for s in query_word_regex if s.strip()]
        if query_word=='^':
            query_word_regex=[]
            
        # print(query_word_term)
        # print(query_word_phrase)
        # print(len(query_word_term),len(query_word_phrase))
        print(query_word_regex)
        if len(query_word_regex)==0:
            query_num=conduct_basic_query(query_word_term=query_word_term,query_word_phrase=query_word_phrase,
                                      query_size=5)
        else:
            query_num=conduct_regex_query(query_word_term=query_word_term,query_word_phrase=query_word_phrase,
                                      query_word_regex=query_word_regex,query_size=5)  
        print(f'Find {query_num} results.')
        print("QUIT to quit (not case sensitive).")
        quit_word=input()
        if quit_word.lower()=="quit":        
            break