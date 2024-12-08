
def get_index():
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
    return index_name,index_body

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