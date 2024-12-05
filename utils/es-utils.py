from elasticsearch import Elasticsearch

es = Elasticsearch(
    hosts=["http://localhost:9200"],
    http_auth=('elastic', '123456')
)

def get_count():
    # 定义索引名称
    index_name='html_index'
    # 查询文档总数
    count_response=es.count(index=index_name)
    print(f"Total documents in index '{index_name}': {count_response['count']}")

def remove_all():
    index_name='html_index'
    delete_response=es.delete_by_query(# 删除所有文档
        index=index_name,
        body={"query": {"match_all": {}}}
    )
    print(f"Deleted documents in index '{index_name}': {delete_response['deleted']}")

if __name__=="__main__":
    get_count()
    remove_all()