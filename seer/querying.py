from elasticsearch import Elasticserach

def return_results(query):
    es = Elasticsearch()
    body = {
        "query": {
            "multi-match": { 
                "query": query,
                "fields": ["text"]
            }
        }
    }
    #body = {"query": {"match": {"body": query}}}
    
    res = es.search(index='privaseer', doc_type='document', body=body)
    print("%d documents found"%res['hits']['total'])
    return res
