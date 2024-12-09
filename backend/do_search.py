from elasticsearch import Elasticsearch
from bs4 import BeautifulSoup
import numpy as np
from collections import Counter
import re
import numpy as np
from flask import Flask,request,jsonify

from query_gen import get_index,gen_query

index_name,index_body=get_index()

#执行搜索
def conduct_query(
    query_word_term=[],
    query_word_phrase=[],
    query_word_regex=[],
    query_domain=None,
    frequent_token=[],
    es=None,
    index_name=index_name,
    fields=['title','anchor','content','url'],
    query_size=5
    ):    
    # print(query_word_phrase+query_word_regex)
    
    query=gen_query(query_word_term=query_word_term,query_word_phrase=query_word_phrase+query_word_regex,
                    fields=fields,frequent_token=frequent_token)

    response=es.search(index=index_name,body=query,scroll='5m',size=10000)#使用滚动方式进行获取
    
    scroll_id=response['_scroll_id']
    results=response['hits']['hits']
    query_len=len(results)
    query_cnt=0
    query_list={}
    result_list=[]
    regex_patterns=[re.compile(regex_word) for regex_word in query_word_regex]
    
    for hit in results:
        if query_cnt>=query_size:
            break
        title=hit['_source']['title']
        content=hit['_source']['content']
        url=hit['_source']['url']
        
        #去除html标签
        soup=BeautifulSoup(content,features="lxml")
        text_content=soup.get_text()

        if len(regex_patterns)>0:
            match_found=any(pattern.search(title) or pattern.search(url) or pattern.search(text_content) for pattern in regex_patterns)
            if not match_found:
                continue
        if (query_domain is not None) and (query_domain not in url):
            continue
        
        query_cnt+=1
        cleaned_content=' '.join(text_content.split()) #去除所有空字符
        print("-"*50)
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
            if token in query_list.keys():
                query_list[token]+=count
            else:
                query_list[token]=count
            print(f"{token}:{count}")
        print("-"*50)
        result_list.append(
            {
                'title':title,
                'utl':url,
                'content':cleaned_content[:250]
            }
        )
    
    while len(results):
        if query_cnt>=query_size:
            break
        response=es.scroll(scroll_id=scroll_id,scroll='5m')
        scroll_id=response['_scroll_id']
        results=response['hits']['hits']
        query_len+=len(results)
        # result_list+=results
        
        for hit in results:
            if query_cnt>query_size:
                break
            title=hit['_source']['title']
            content=hit['_source']['content']
            url=hit['_source']['url']
            
            soup=BeautifulSoup(content,features="lxml")
            text_content=soup.get_text()
            
            if len(regex_patterns)>0:
                match_found=any(pattern.search(title) or pattern.search(url) or pattern.search(text_content) for pattern in regex_patterns)
                if not match_found:
                    continue
            
            if (query_domain is not None) and (query_domain not in url):
                continue
            
            query_cnt+=1
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
                if token in query_list.keys():
                    query_list[token]+=count
                else:
                    query_list[token]=count
                print(f"{token}:{count}")
            result_list.append(
                {
                    'title':title,
                    'utl':url,
                    'content':cleaned_content[:250]
                }
            )
                
    # return query_cnt,query_list,result_list
    return query_cnt,query_list,result_list

if __name__=="__main__":
    query_word_term=['程明明']
    query_word_phrase=[]
    query_word_regex=[]
    query_domain='weekly.nankai.edu.cn'
    frequent_token=['华为']
    
    es = Elasticsearch(
        hosts=["http://localhost:9200"],
        http_auth=('elastic', '123456')
    )
    
    query_cnt,query_list,result_list=conduct_query(query_word_term=query_word_term,
    query_word_phrase=query_word_phrase,query_word_regex=query_word_regex,query_domain=query_domain,frequent_token=['华为'],
    es=es,index_name=index_name,fields=['title','anchor','content','url'],query_size=5)
    
    recommend_cnt,recommend_list,recommend_res=conduct_query(query_word_term=query_word_term,
    query_word_phrase=query_word_phrase+query_word_term,query_word_regex=query_word_regex,query_domain=query_domain,frequent_token=['华为'],
    es=es,index_name=index_name,fields=['title','anchor','content','url'],query_size=5)
    
    print(query_cnt)
    print(query_list)
    print(result_list)