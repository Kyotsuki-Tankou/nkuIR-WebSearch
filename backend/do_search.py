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
    query_size=5,
    used_list=[]
    ):    
    # print(query_word_phrase+query_word_regex)
    print(f'frequent_token: {frequent_token}')
    
    query=gen_query(query_word_term=query_word_term,query_word_phrase=query_word_phrase+query_word_regex,
                    fields=fields,frequent_token=frequent_token)
    # print(query)
    # explain=es.explain(index=index_name,body=query,id='lKFGppMBlHQZ9_c9sXxq')
    # print(explain)
    response=es.search(index=index_name,body=query,scroll='5m',size=1000)#使用滚动方式进行获取
    
    scroll_id=response['_scroll_id']
    results=response['hits']['hits']
    query_len=len(results)
    query_cnt=0
    query_list={}
    result_list=[]
    used_url=[]
    regex_patterns=[re.compile(regex_word) for regex_word in query_word_regex]
    
    for hit in results:
        if query_cnt>=query_size:
            break
        title=hit['_source']['title']
        content=hit['_source']['content']
        url=hit['_source']['url']
        # id=hit['_id']
        # print(f'id:{id}')
        # print(f"explain:{explain}")
        #去除html标签
        soup=BeautifulSoup(content,features="lxml")
        text_content=soup.get_text()

        if len(regex_patterns)>0:
            match_found=any(pattern.search(title) or pattern.search(url) or pattern.search(text_content) for pattern in regex_patterns)
            if not match_found:
                continue
        if (query_domain is not None) and (query_domain not in url):
            continue
        if url in used_list:
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
        used_url.append(url)
        result_list.append(
            {
                'title':title,
                'url':url,
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
            if url in used_list:
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
                    'url':url,
                    'content':cleaned_content[:250]
                }
            )
            used_url.append(url)
                
    # return query_cnt,query_list,result_list
    return query_cnt,query_list,result_list,used_url
    # return 0,[],[]

def word_proc(query_word):
    query_word_term=list(set(query_word.split('^')))
    query_word_term=[s for s in query_word_term if s.strip()]
    if query_word=='^':
        query_word_term=[]
    return query_word_term
    
if __name__=="__main__":
    query_word_term=['程明明']
    query_word_phrase=[]
    query_word_regex=[]
    query_domain=''
    frequent_token=['']
    
    es = Elasticsearch(
        hosts=["http://localhost:9200"],
        http_auth=('elastic', '123456')
    )
    
    query_cnt,query_list,result_list,used_url=conduct_query(query_word_term=query_word_term,
    query_word_phrase=query_word_phrase,query_word_regex=query_word_regex,query_domain=query_domain,frequent_token=['CT影像AI筛查助力疫情防控'],
    es=es,index_name=index_name,fields=['title','anchor','content','url'],query_size=5)
    
    # recommend_cnt,recommend_list,recommend_res=conduct_query(query_word_term=query_word_term,
    # query_word_phrase=query_word_phrase+query_word_term,query_word_regex=query_word_regex,query_domain=query_domain,frequent_token=['华为'],
    # es=es,index_name=index_name,fields=['title','anchor','content','url'],query_size=5,used_list=used_url)
    
    print(query_cnt)
    print(query_list)
    print(result_list)