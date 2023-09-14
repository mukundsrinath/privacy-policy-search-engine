from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from elasticsearch import Elasticsearch
from . import models
import time
import json

# Create your views here.

def hello(request):
    return HttpResponse("Hello World")

def search(request):
    return render(request, 'seer/index.html')
	
def about(request):
    return render(request, 'seer/about.html')
		
def contact_us(request):
    return render(request, 'seer/contact.html')
	
def store(request):
    try:
        contact = {}
        contact['first_name'] = request.POST.get('first_name')
        contact['last_name'] = request.POST.get('last_name')
        contact['email'] = request.POST.get('email')
        contact['subject'] = request.POST.get('subject')
        contact['content'] = request.POST.get('content')
        ts = time.time()
        with open('C:/Users/Mukund/Desktop/privaseer/'+str(ts).replace('.', '_'), 'w+') as f:
            f.write(json.dumps(contact))
        return render(request, 'seer/contact.html', {'errormessage': 'Your response has been recorded. Thank you.'})
    except:
        return render(request, 'seer/contact.html', {'errormessage': 'An error occured. Please try again'})
	
es = Elasticsearch()

def pre_query(request):
    if request.method == 'POST':
        q = request.POST.get('q')
        c = request.POST.get('choice')
        start = 0
        if q != None:
            return query(request, q, c, start)
        else:
            return render(request, 'seer/index.html', {'errormessage': 'Please enter a query'})
    else:
        start = int(request.GET.get('start', 0))
        c = request.GET.get('choice')
        q = request.GET.get('q', None)
        if start == 0 or q == None:
            return render(request, 'seer/index.html')
        else:
            return query(request, q, c, start)

def query(request, query, choice, start):
    
    #size=10
    body = {}
    #body['from'] = start
    #body['size'] = size
    body = {}
    body['query'] = {}
    body['query']['match'] = {}
    body['query']['match']['text'] = query
    #body['function_score']['query']['bool'] = {}
    #body['function_score']['query']['bool']['must'] = [None]
    #body['function_score']['query']['bool']['must'][0] = {}
    #body['function_score']['query']['bool']['must'][0]['multi_match'] = {}
    #body['function_score']['query']['bool']['must'][0]['multi_match']['query'] = query
    #if choice == 'title-text':
    #    body['function_score']['query']['bool']['must'][0]['multi_match']['fileds'] = ['title', 'text']
    #else:
    #    body['function_score']['query']['bool']['must'][0]['multi_match']['fileds'] = ['urls']
    #body['function_score']['query']['bool']['must'][0]['multi_match']['operator'] = 'and'		
    #body['function_score']['query']['bool']['filter'] = [None]
    #body['function_score']['query']['bool']['filter'][0] = {}
    #body['function_score']['query']['bool']['filter'][0]['range'] = {}
    #body['function_score']['query']['bool']['filter'][0]['range']['readability'] = {}
    #body['function_score']['query']['bool']['filter'][0]['range']['readability']['gte'] = -100
    #body['function_score']['query']['bool']['filter'][0]['range']['readability']['lte'] = 500
    #body['function_score']['script_score'] = {}
    #body['function_score']['script_score']['script'] = {}
    #body['function_score']['script_score']['script']['params'] = {}
    #body['function_score']['script_score']['script']['params']['a'] = 2
    #body['function_score']['script_score']['script']['params']['b'] = 2
    #body['function_score']['script_score']['source'] = "Math.log(params.a + doc['pagerank'].value)"
    #body['highlight'] = {}
    #body['highlight']['fields'] = {}
    #if choice == 'title-text':
    #    body['highlight']['fields']['text'] = {}
    count_body = {}
    count_body['query'] = {}
    count_body['query']['bool'] = {}
    count_body['query']['bool']['must'] = [None]
    count_body['query']['bool']['must'][0] = {}
    count_body['query']['bool']['must'][0]['multi_match'] = {}
    count_body['query']['bool']['must'][0]['multi_match']['query'] = query
    if choice == 'title-text':
        count_body['query']['bool']['must'][0]['multi_match']['fields'] = ['title', 'text']
    else:
        body['function_score']['query']['bool']['must'][0]['multi_match']['fields'] = ['urls']
    count_body['query']['bool']['must'][0]['multi_match']['operator'] = 'and'
    count_body['query']['bool']['filter'] = [None]
    count_body['query']['bool']['filter'][0] = {}
    count_body['query']['bool']['filter'][0]['range'] = {}
    count_body['query']['bool']['filter'][0]['range']['readability'] = {}
    count_body['query']['bool']['filter'][0]['range']['readability']['gte'] = -100
    count_body['query']['bool']['filter'][0]['range']['readability']['lte'] = 500
	
#    if choice == 'title-text':
#        body = {
#            "from": start,
#            "size": size,
#            "query": {
#                "bool": {"must": [
#                    {
#                        "multi_match": {
#                            "query": query,
#                            "fields": ["title", "text"],
#                            "operator": "and"
#                        }
#                    }],
#                    "should": [
#                    {
#                        "rank_feature": {
#                            "field":"pagerank",
#                            "log": {"scaling_factor": 10}
#                        },
#                    }
#                ]}
#            },
#            'highlight': {'fields': {'text': {}}}
#        }
#
#        count_body = {
#            "query": {
#                "multi_match": {
#                    "query": query,
#                    "fields": ["text", "title"],
#                    "operator": "and"
#                }
#            },
#        }
#
#    else:
#        body = {
#            "from": start,
#            "size": size,
#            "query": {
#                "bool": {"must": [
#                    {
#                        "multi_match": {
#                            "query": query,
#                            "fields": ["url"],
#                            "operator": "and"
#                        }
#                    }],   
#                    "should": [{
#                        "rank_feature": {
#                            "field":"pagerank",
#                            "log": {"scaling_factor": 10}
#                        },
#                    }
#                ]}
#            }
#        }
#        count_body = {
#            "query": {
#                "multi_match": {
#                    "query": query,
#                    "fields": ["url"],
#                    "operator": "and"
#                }
#            }
#        }
#    print(json.dumps(body))          
    results = es.search(index='pos_privaseer', body=body)
    #count = es.count(index='pos_privaseer', body=count_body)
    if not results.get('hits'):
        return render('seer/error.html',{'errormessage':'Your query returned zero results, please try another query'})
    else:
        #totalresultsNumFound= count["count"]
        totalresultsNumFound=0
        #hlresults=r.json()['highlighting']
        results=results['hits']['hits']
        #print(res['hits']['hits'])
        SearchResults=[] 
        if len(results) > 0:
            for result in results:
                resultid= result['_id']
                f = models.SearchResult(resultid) #calling the object class that is defined inside models.py

                f.content= result['_source']['text']
                    
                    
                    # rawpath= result['_source']['file']['url']
                    
                    #removing local folder path
                f.url= result['_source']['url']
                f.title = result['_source']['title']
                #f.description = str(result['_source']['meta']['raw']['description'])
                f.description = ''
                if 'highlight' in result:
                    for desc in result['highlight']['text']:
                        f.description = f.description + desc + '\n'

                #f.description = " ".join(f.description).encode("utf-8")
                #    '''
                #    if len(result.get('category',[])) > 0:
                #       f.category=result['category'][0].encode("utf-8") 
                #    '''
                #trying to use the location field to get the file name to display the image
                #f.filename= str(imageid)+'.png'
                SearchResults.append(f)
                
            return render(request, 'seer/htmlresult.html', {'results':SearchResults ,'q': query,\
                       'total':totalresultsNumFound, 'i':str(start+1) , 'j':str(len(results)+start), 'choice': choice})
        else:
            return render(request, 'seer/error.html',{'errormessage':'Your search returned zero results, please try another query'})

