
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
                "content": {"type": "text", "analyzer": "ik_analyzer"},
                "pagerank": {"type": "float"}
            }
        }
    }
    return index_name,index_body

def gen_query(query_word_term, query_word_phrase, fields, frequent_token):
    # 生成基础查询

    # 精准匹配 "南开大学" -> "南开大学"
    must_clauses = []
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

    # 模糊匹配 "南开大学" -> "南开是大学" 或 "南"
    should_clauses = []
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

    # 对 frequent_token 添加查询加分逻辑
    frequent_token_clauses = []
    for token in frequent_token:
        frequent_token_clauses.append(
            {
                "bool": {
                    "should": [
                        {"match": {"content": token}},
                        {"match": {"title": token}}
                    ],
                    "minimum_should_match": 1
                }
            }
        )

    query = {
        "query": {
            "function_score": {  # 进行 function_score 查询
                "query": {  # 查询主体
                    "bool": {
                        "must": must_clauses,
                        "should": should_clauses + frequent_token_clauses
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
                        "weight": 2.0,  # 针对 frequent_token 的加分
                        "filter": {
                            "bool": {
                                "should": [
                                    {"match": {"content": token}} for token in frequent_token
                                ] + [
                                    {"match": {"title": token}} for token in frequent_token
                                ]
                            }
                        }
                    }
                ],
                "boost_mode": "sum",
                "max_boost": 20.0  # 最多提高10个 token 的权重
            }
        },
        "highlight":{
            "fields":{
                field:{} for field in fields
            }
        }
    }

    return query