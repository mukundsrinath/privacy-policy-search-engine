from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.core.mail import send_mail
from elasticsearch import Elasticsearch
import urllib
import urllib.request
from . import models
import time
import json

def hello(request):
    return HttpResponse("Hello World")

def search(request):
    return render(request, 'seer/index.html')
	
def about(request):
    return render(request, 'seer/about.html')
		
def contact_us(request):
    return render(request, 'seer/contact.html')

def data(request):
    return render(request, 'seer/data.html')

def publications(request):
    return render(request, 'seer/publications.html')

def people(request):
    return render(request, 'seer/people.html')

def news(request):
    return render(request, 'seer/news.html')

def robots(request):
    file = open('/data/privaseer/seer/templates/seer/robots.txt', 'r')
    content = file.read()
    file.close()
    return HttpResponse(content, content_type='text/plain')
	
def store(request):
    recaptcha_response = request.POST.get('g-recaptcha-response')
    url = 'https://www.google.com/recaptcha/api/siteverify'
    values = { 'secret': '6LfdVfIcAAAAAEGnI-b6wuwY7N21NYUi6VB9JW7M', 'response': recaptcha_response }
    data = urllib.parse.urlencode(values).encode()
    req =  urllib.request.Request(url, data=data)
    response = urllib.request.urlopen(req)
    result = json.loads(response.read().decode())
    if result['success']:
        contact = {}
        contact['first_name'] = request.POST.get('first_name')
        contact['last_name'] = request.POST.get('last_name')
        contact['email'] = request.POST.get('email')
        contact['subject'] = request.POST.get('subject')
        contact['content'] = request.POST.get('content')
        content = 'First Name: ' + contact['first_name'] + '\n' + "Last name: " + contact['last_name'] + '\n' + "Body: " + contact['content']
        try:
            send_mail(contact['subject'], content, contact['email'], ['clg20@psu.edu','shomir@psu.edu','mus824@psu.edu'])
            return render(request, 'seer/contact.html', {'errormessage': 'Your response has been recorded. Thank you.'})
        except Exception as e:
            print(e)
            print('Could not send mail')
            return render(request, 'seer/contact.html', {'errormessage': 'An error occured. Please try again'})
        try:
            ts = time.time()
            with open('/data/privaseer/contacts/'+str(ts).replace('.', '_'), 'w+') as f:
                f.write(json.dumps(contact))
            return render(request, 'seer/contact.html', {'errormessage': 'Your response has been recorded. Thank you.'})
        except Exception as e:
            print(e)
            return render(request, 'seer/contact.html', {'errormessage': 'An error occured. Please try again'})
    else:
        return render(request, 'seer/contact.html', {'errormessage': 'Invalid reCAPTCHA. Please try again.'})
def privacy_policy(request):
    return render(request, 'seer/privacy.html')
	
es = Elasticsearch()

def pre_query(request):
    if request.method == 'POST':
        q = request.POST.get('q')
        c = request.POST.get('choice')
        industry = request.GET.getlist('industry', [])
        tracktech = request.GET.getlist('tracktech', [])
        selfreg = request.GET.getlist('selfreg', [])
        regagree = request.GET.getlist('regagree', [])
        crawldates = request.GET.getlist('crawldates',[])
        start = 0
        if not q or q.strip() == '':
            return render(request, 'seer/index.html', {'errormessage': 'Please enter a query'}) 
        try:
            return query(request, q, c, start, industry, -10, 100, 0, 1, "customrank", tracktech, selfreg, regagree, crawldates)
        except:
            return render(request, 'seer/index.html', {'errormessage': 'Please enter a query'})
    else:
        start = int(request.GET.get('start', 0))
        c = request.GET.get('choice')
        q = request.GET.get('q', None)
        industry = request.GET.getlist('industry', [])
        tracktech = request.GET.getlist('tracktech', [])
        selfreg = request.GET.getlist('selfreg', [])
        regagree = request.GET.getlist('regagree', [])
        crawldates = request.GET.getlist('crawldates', [])
        gte = request.GET.get('read_gte')
        lte = request.GET.get('read_lte')
        if gte == '':
            gte = -10
        if lte == '':
            lte = 100
        vague_gte = request.GET.get('vague_gte')
        vague_lte = request.GET.get('vague_lte')
        if vague_gte == '':
            vague_gte = 0
        if vague_lte == '':
            vague_lte = 1
        sortby = request.GET.get('sortby')
        if q == None:
            return render(request, 'seer/index.html')
        else:
            try:
                return query(request, q, c, start, industry, gte, lte, vague_gte, vague_lte, sortby, tracktech, selfreg, regagree, crawldates)
            except:
                return render(request, 'seer/index.html', {'errormessage': 'Please enter a query'})

def query(request, query, choice, start, industry, gte, lte, vague_gte, vague_lte, sortby, tracktech, selfreg, regagree, crawldates):
    print(crawldates)
    size=10
    body = {}
    body['from'] = start
    body['size'] = size
    body['query'] = {}
    body['query']['function_score'] = {}
    body['query']['function_score']['query'] = {}
    body['query']['function_score']['query']['bool'] = {}
    body['query']['function_score']['query']['bool']['must'] = [None]
    body['query']['function_score']['query']['bool']['must'][0] = {}
    body['query']['function_score']['query']['bool']['must'][0]['query_string'] = {}
    body['query']['function_score']['query']['bool']['must'][0]['query_string']['query'] = query
    body['query']['function_score']['query']['bool']['must'][0]['query_string']['default_operator'] = 'AND'
    if choice == 'title-text':
        body['query']['function_score']['query']['bool']['must'][0]['query_string']['default_field'] = 'text'
    else:
        body['query']['function_score']['query']['bool']['must'][0]['query_string']['default_field'] = 'url'
    #body['query']['function_score']['query']['bool']['must'][0]['multi_match']['operator'] = 'and'
    filter_dict = {}
    filter_index = 1
    filters = [[tracktech,'tracktech'],[selfreg, 'selfreg'], [regagree, 'regagree'], [industry, 'industry'], [crawldates, 'crawldates']]
    for filter in filters:
        if filter[0] != []:
            filter_index += 1
            filter_dict[filter[1]] = filter_index
    filter_lst = [None]*(filter_index+1)

    body['query']['function_score']['query']['bool']['filter'] = filter_lst
    #body['query']['function_score']['query']['bool']['filter'] = [None]
    
    body['query']['function_score']['query']['bool']['filter'][0] = {}
    body['query']['function_score']['query']['bool']['filter'][0]['range'] = {}
    body['query']['function_score']['query']['bool']['filter'][0]['range']['readability'] = {}
    body['query']['function_score']['query']['bool']['filter'][0]['range']['readability']['gte'] = gte
    body['query']['function_score']['query']['bool']['filter'][0]['range']['readability']['lte'] = lte

    body['query']['function_score']['query']['bool']['filter'][1] = {}
    body['query']['function_score']['query']['bool']['filter'][1]['range'] = {}
    body['query']['function_score']['query']['bool']['filter'][1]['range']['vagueness'] = {}
    body['query']['function_score']['query']['bool']['filter'][1]['range']['vagueness']['gte'] = vague_gte
    body['query']['function_score']['query']['bool']['filter'][1]['range']['vagueness']['lte'] = vague_lte
    
    filterfields = [[tracktech,'tracktech','tracking_tech'],[selfreg, 'selfreg','self_regulatory_bodies'], [regagree, 'regagree','agreements_regulations'], [crawldates, 'crawldates', 'crawl_date']]

    for filterfield in filterfields:
        if filterfield[0] != []:
            index = filter_dict[filterfield[1]]
            body['query']['function_score']['query']['bool']['filter'][index] = {}
            body['query']['function_score']['query']['bool']['filter'][index]['terms'] = {}
            body['query']['function_score']['query']['bool']['filter'][index]['terms'][filterfield[2]] = filterfield[0]

    hierarchy = set_industry_hierarchy()
    if industry != []:
        index = filter_dict['industry']
        body['query']['function_score']['query']['bool']['filter'][index] = {}
        body['query']['function_score']['query']['bool']['filter'][index]['terms'] = {}
        industry_list = []
        for item in industry:
            industry_list.extend(hierarchy[item])
        body['query']['function_score']['query']['bool']['filter'][index]['terms']['industry'] = industry_list

    body['query']['function_score']['script_score'] = {}
    body['query']['function_score']['script_score']['script'] = {}
    body['query']['function_score']['script_score']['script']['params'] = {}
    #body['query']['function_score']['script_score']['script']['params']['a'] = 2
    #body['query']['function_score']['script_score']['script']['params']['b'] = 2
    #body['query']['function_score']['script_score']['script']['source'] = "Math.log(params.a + doc['pagerank'].value)"
    body['query']['function_score']['script_score']['script']['params']['a'] = 10
    body['query']['function_score']['script_score']['script']['params']['b'] = 5
    body['query']['function_score']['script_score']['script']['params']['c'] = 1000
    if sortby == "querysim":
        body['query']['function_score']['script_score']['script']['source'] = "_score" ####for query similarity ranking
    elif sortby == "pagerank":
        body['query']['function_score']['script_score']['script']['source'] = "Math.log10(doc['pagerank'].value)" ####for pagerank ranking
    else: #change
        body['query']['function_score']['script_score']['script']['source'] = "_score * doc['probability'].value * Math.log10(doc['pagerank'].value)"


    body['query']['function_score']['boost_mode'] = "replace"
    if choice == 'title-text':
        body['highlight'] = {}
        body['highlight']['fields'] = {}
        body['highlight']['fields']['text'] = {}

    results = es.search(index='privaseer_linkedin_2023', body=body)
    print(body)
    #print(results)

    count_body = {}
    count_body['query'] = {}
    count_body['query']['bool'] = {}
    count_body['query']['bool']['must'] = [None]
    count_body['query']['bool']['must'][0] = {}
    count_body['query']['bool']['must'][0]['query_string'] = {}
    count_body['query']['bool']['must'][0]['query_string']['query'] = query
    count_body['query']['bool']['must'][0]['query_string']['default_operator'] = 'AND'
    if choice == 'title-text':
        count_body['query']['bool']['must'][0]['query_string']['default_field'] = 'text'
    else:
        count_body['query']['bool']['must'][0]['query_string']['default_field'] = 'url'
    #count_body['query']['bool']['must'][0]['multi_match']['operator'] = 'and'
    
    count_body['query']['bool']['filter'] = filter_lst

    count_body['query']['bool']['filter'][0] = {}
    count_body['query']['bool']['filter'][0]['range'] = {}
    count_body['query']['bool']['filter'][0]['range']['readability'] = {}
    count_body['query']['bool']['filter'][0]['range']['readability']['gte'] = gte
    count_body['query']['bool']['filter'][0]['range']['readability']['lte'] = lte

    count_body['query']['bool']['filter'][1] = {}
    count_body['query']['bool']['filter'][1]['range'] = {}
    count_body['query']['bool']['filter'][1]['range']['vagueness'] = {}
    count_body['query']['bool']['filter'][1]['range']['vagueness']['gte'] = vague_gte
    count_body['query']['bool']['filter'][1]['range']['vagueness']['lte'] = vague_lte 

    for filterfield in filterfields: 
        if filterfield[0] != []:
            index = filter_dict[filterfield[1]]
            count_body['query']['bool']['filter'][index] = {}
            count_body['query']['bool']['filter'][index]['terms'] = {}
            count_body['query']['bool']['filter'][index]['terms'][filterfield[2]] = filterfield[0]

    if industry != []:
        index = filter_dict['industry']
        count_body['query']['bool']['filter'][index] = {}
        count_body['query']['bool']['filter'][index]['terms'] = {}
        count_body['query']['bool']['filter'][index]['terms']['industry'] = industry_list 

    industry_body = {}
    industry_body['query'] = {}
    industry_body['query']['bool'] = {}
    industry_body['query']['bool']['must'] = [None]
    industry_body['query']['bool']['must'][0] = {}
    industry_body['query']['bool']['must'][0]['query_string'] = {}
    industry_body['query']['bool']['must'][0]['query_string']['query'] = query
    industry_body['query']['bool']['must'][0]['query_string']['default_operator'] = 'AND'
    if choice == 'title-text':
        industry_body['query']['bool']['must'][0]['query_string']['default_field'] = 'text'
    else:
        industry_body['query']['bool']['must'][0]['query_string']['default_field'] = 'url'

    industry_body['query']['bool']['filter'] = [None] * filter_index if 'industry' in filter_dict else [None] * (filter_index + 1)

    industry_body['query']['bool']['filter'][0] = {}
    industry_body['query']['bool']['filter'][0]['range'] = {}
    industry_body['query']['bool']['filter'][0]['range']['readability'] = {}
    industry_body['query']['bool']['filter'][0]['range']['readability']['gte'] = gte
    industry_body['query']['bool']['filter'][0]['range']['readability']['lte'] = lte 

    industry_body['query']['bool']['filter'][1] = {}
    industry_body['query']['bool']['filter'][1]['range'] = {}
    industry_body['query']['bool']['filter'][1]['range']['vagueness'] = {}
    industry_body['query']['bool']['filter'][1]['range']['vagueness']['gte'] = vague_gte
    industry_body['query']['bool']['filter'][1]['range']['vagueness']['lte'] = vague_lte

    for filterfield in filterfields:
        if filterfield[0] != []:
            index = filter_dict[filterfield[1]]
            industry_body['query']['bool']['filter'][index] = {}
            industry_body['query']['bool']['filter'][index]['terms'] = {}
            industry_body['query']['bool']['filter'][index]['terms'][filterfield[2]] = filterfield[0]

    industry_hierarchy = get_industry_bucket(industry_body['query'], hierarchy)
    results = es.search(index='privaseer_linkedin_2023', body=body)
    #print(results)
    #results = []
    count = es.count(index='privaseer_linkedin_2023', body=count_body)
    print("count "+str(count))
    #exit()
    if not results.get('hits'):
        return render('seer/error.html',{'errormessage':'Your query returned zero results, please try another query'})
    else:
        totalresultsNumFound= count["count"]
        #hlresults=r.json()['highlighting']
        results=results['hits']['hits']
        industry_hierarchy_list = []
        for item in industry_hierarchy:
            item['key'] = item['key'].capitalize()
            for sub in item['sub']:
               sub['key'] = sub['key'].capitalize()
            industry_hierarchy_list.append(item)
        #print(res['hits']['hits'])
        SearchResults=[] 
        if len(results) > 0:
            for result in results:
                resultid= result['_id']
                f = models.SearchResult(resultid) #calling the object class that is defined inside models.py

                f.content= result['_source']['text']
                f.url= result['_source']['url']
                f.title = result['_source']['title']
                f.date = result['_source']['display_date']
                #f.description = str(result['_source']['meta']['raw']['description'])
                f.description = ''
                if result['_source']['industry'] == 'nan':
                    f.industry = 'Unknown'
                else:
                    f.industry = result['_source']['industry'].capitalize()
                if 'highlight' in result:
                    for desc in result['highlight']['text']:
                        f.description = f.description + desc + '\n'

                SearchResults.append(f)
                
            return render(request, 'seer/htmlresult.html', {'results':SearchResults ,'industry_buckets': industry_hierarchy_list,'q': query,\
                       'total':totalresultsNumFound, 'i':str(start+1) , 'j':str(len(results)+start), 'choice': choice})
        else:
            return render(request, 'seer/error.html',{'errormessage':'Your search returned zero results, please try another query', 'q': query, 'choice':choice})

def get_industry_bucket(query_body, hierarchy):
    industry_tld_dict = map_industry_toplevel()
    all_buckets = get_all_buckets(industry_tld_dict)
    body = {
        "size": 0,
        "query": query_body,
        "aggs": {
            "industry": {
                "terms": {
                    "field": "industry",
                    "size": 200
                }
            }
        }
    }
    response = es.search(index='privaseer_linkedin_2023', body=body)
    industry_buckets = response['aggregations']['industry']['buckets']
    industry_hierarchy = build_industry_hierarchy(industry_buckets, hierarchy, all_buckets, industry_tld_dict)
    return industry_hierarchy

def get_all_buckets(industry_tld_dict):
    body = {
        "size": 0,
        "aggs": {
            "industry": {
                "terms": {
                    "field": "industry",
                    "size": 200
                }
            }
        }
    }
    response = es.search(index='privaseer_linkedin_2023', body=body)
    all_buckets = response['aggregations']['industry']['buckets']
    all_buckets_dict = {}
    for item in all_buckets:
        all_buckets_dict[item['key']] = item['doc_count']
    output = {}
    for item in all_buckets:
        tld = industry_tld_dict[item['key']]
        output[tld] = output.get(tld, 0) + all_buckets_dict[item['key']]    
    return output

def build_industry_hierarchy(industry_buckets, hierarchy_dict, all_buckets_dict, industry_tld_dict):
    result = []
    result_dict = {}
    industry_buckets_dict = {}
    for item in industry_buckets:
        industry_buckets_dict[item['key']] = item['doc_count']
    for item in industry_buckets:
        tld = industry_tld_dict[item['key']]
        if tld not in result_dict: 
            count = item['doc_count']
            result_dict[tld] = {'count': count, 'sub': [{'key': item['key'], 'count': item['doc_count']}], 
              'percentage': 0 if all_buckets_dict[tld] == 0 else round((count/all_buckets_dict[tld])*100, 2)}
        else:
            count = result_dict[tld]['count'] + item['doc_count']
            result_dict[tld]['count'] = count
            result_dict[tld]['sub'].append({'key': item['key'], 'count': item['doc_count']})
            result_dict[tld]['percentage'] = 0 if all_buckets_dict[tld] == 0 else round((count/all_buckets_dict[tld])*100, 2)

    for tld in sorted(result_dict, key=lambda x: result_dict[x]['percentage'], reverse=True):
        result.append({'key': tld, 'count': result_dict[tld]['count'], 'sub': result_dict[tld]['sub'], 'percentage': result_dict[tld]['percentage']})    
    return result

def set_industry_hierarchy():
    output = {}
    #top-level
    output['nan'] = []
    output['information technology & electronics'] = []
    output['medical'] = []
    output['civil, mechanical & electrical'] = []
    output['education'] = []
    output['finance, marketing & human resources'] = []
    output['non-profit'] = []
    output['travel, food & hospitality'] = []
    output['sports, media & entertainment'] = []
    output['government, defense & legal'] = []
    output['consumer & supply chain'] = []
    #sub
    output['nan'] = ['nan']
 
    output['information technology & electronics'] = ['information technology and services', 'computer software', 'internet', 'telecommunications', 
    'consumer electronics', 'information services', 'computer & network security', 'computer hardware', 'computer networking', 'semiconductors', 
    'wireless', 'program development', 'nanotechnology']

    output['medical'] = ['health, wellness and fitness', 'hospital & health care', 'medical practice', 'medical devices', 'pharmaceuticals', 
    'biotechnology', 'mental health care', 'veterinary', 'alternative medicine']

    output['civil, mechanical & electrical'] = ['automotive', 'electrical/electronic manufacturing', 'mechanical or industrial engineering', 
    'oil & energy', 'machinery', 'building materials', 'renewables & environment', 'architecture & planning', 'chemicals', 'industrial automation', 
    'utilities', 'mining & metals', 'airlines/aviation', 'civil engineering', 'aviation & aerospace', 'glass, ceramics & concrete', 
    'paper & forest products', 'shipbuilding', 'railroad manufacture', 'construction']

    output['education'] = ['education management', 'professional training & coaching', 'publishing', 'e-learning', 'higher education', 
    'research', 'primary/secondary education', 'writing and editing', 'market research', 'libraries', 'think tanks', 'translation and localization',
    'museums and institutions']

    output['finance, marketing & human resources'] = ['marketing and advertising', 'financial services', 'real estate', 'management consulting', 
    'insurance', 'accounting', 'investment management', 'banking', 'commercial real estate', 'venture capital & private equity', 
    'outsourcing/offshoring', 'import and export', 'investment banking', 'capital markets', 'staffing and recruiting', 'human resources']

    output['non-profit'] = ['non-profit organization management', 'environmental services', 'philanthropy', 'fund-raising', 'public safety', 
    'nonprofit organization management']

    output['travel, food & hospitality'] = ['hospitality', 'leisure, travel & tourism', 'food & beverages', 'restaurants', 'wine and spirits', 
    'gambling & casinos']

    output['sports, media & entertainment'] = ['entertainment', 'sports', 'events services', 'media production', 'music', 'online media', 
    'sporting goods', 'photography', 'broadcast media', 'graphic design', 'computer games', 'recreational facilities and services', 
    'motion pictures and film', 'animation', 'newspapers', 'public relations and communications', 'fine art', 'performing arts', 'printing']

    output['government, defense & legal'] = ['law practice', 'legal services', 'civic & social organization', 'security and investigations', 
    'government administration', 'religious institutions', 'defense & space', 'public policy', 'political organization', 'government relations', 
    'international affairs', 'law enforcement', 'judiciary', 'legislative office', 'military', 'alternative dispute resolution', 'executive office']

    output['consumer & supply chain'] = ['retail', 'apparel & fashion', 'design', 'consumer goods', 'consumer services', 'wholesale', 
    'facilities services', 'furniture', 'food production', 'business supplies and equipment', 'logistics and supply chain', 'individual & family services',
    'luxury goods & jewelry', 'packaging and containers', 'plastics', 'package/freight delivery', 'dairy', 'supermarkets', 'fishery', 
    'international trade and development', 'cosmetics', 'farming', 'textiles', 'warehousing', 'tobacco', 'ranching', 'transportation/trucking/railroad',
    'maritime', 'arts and crafts']  

    return output

def map_industry_toplevel():
    
    output = {'nan': 'nan', 
    'information technology and services': 'information technology & electronics', 'computer software' : 'information technology & electronics',
    'internet': 'information technology & electronics', 'telecommunications': 'information technology & electronics', 
    'consumer electronics': 'information technology & electronics', 'information services': 'information technology & electronics', 
    'computer & network security': 'information technology & electronics', 'computer hardware': 'information technology & electronics', 
    'computer networking': 'information technology & electronics', 'semiconductors': 'information technology & electronics', 'wireless': 'information technology & electronics', 
    'program development': 'information technology & electronics', 'nanotechnology': 'information technology & electronics',
    'health, wellness and fitness': 'medical', 'hospital & health care': 'medical', 'medical practice': 'medical', 'medical devices': 'medical', 
    'pharmaceuticals': 'medical', 'biotechnology': 'medical', 'mental health care': 'medical', 'veterinary': 'medical', 'alternative medicine': 'medical',
    'automotive': 'civil, mechanical & electrical', 'electrical/electronic manufacturing': 'civil, mechanical & electrical', 
    'mechanical or industrial engineering': 'civil, mechanical & electrical', 'oil & energy': 'civil, mechanical & electrical', 
    'machinery': 'civil, mechanical & electrical', 'building materials': 'civil, mechanical & electrical', 'renewables & environment': 'civil, mechanical & electrical', 
    'architecture & planning': 'civil, mechanical & electrical', 'chemicals': 'civil, mechanical & electrical', 'industrial automation': 'civil, mechanical & electrical', 
    'utilities': 'civil, mechanical & electrical', 'mining & metals': 'civil, mechanical & electrical', 'airlines/aviation': 'civil, mechanical & electrical', 
    'civil engineering': 'civil, mechanical & electrical', 'aviation & aerospace': 'civil, mechanical & electrical', 'glass, ceramics & concrete': 'civil, mechanical & electrical', 
    'paper & forest products': 'civil, mechanical & electrical', 'shipbuilding': 'civil, mechanical & electrical', 
    'railroad manufacture': 'civil, mechanical & electrical', 'construction': 'civil, mechanical & electrical',
    'education management': 'education', 'professional training & coaching': 'education', 'publishing': 'education', 'e-learning': 'education', 
    'higher education': 'education', 'research': 'education', 'primary/secondary education': 'education', 'writing and editing': 'education', 
    'market research': 'education', 'libraries': 'education', 'think tanks': 'education', 'translation and localization': 'education',
    'museums and institutions': 'education', 'marketing and advertising': 'finance, marketing & human resources', 
    'financial services': 'finance, marketing & human resources', 'real estate': 'finance, marketing & human resources', 
    'management consulting': 'finance, marketing & human resources', 'insurance': 'finance, marketing & human resources', 
    'accounting': 'finance, marketing & human resources', 'investment management': 'finance, marketing & human resources', 
    'banking': 'finance, marketing & human resources', 'commercial real estate': 'finance, marketing & human resources', 
    'venture capital & private equity': 'finance, marketing & human resources', 'outsourcing/offshoring': 'finance, marketing & human resources', 
    'import and export': 'finance, marketing & human resources', 'investment banking': 'finance, marketing & human resources', 
    'capital markets': 'finance, marketing & human resources', 'staffing and recruiting': 'finance, marketing & human resources', 
    'human resources': 'finance, marketing & human resources', 'non-profit organization management': 'non-profit', 'environmental services': 'non-profit',
    'philanthropy': 'non-profit', 'fund-raising': 'non-profit', 'public safety': 'non-profit', 'nonprofit organization management': 'non-profit',
    'hospitality': 'travel, food & hospitality', 'leisure, travel & tourism': 'travel, food & hospitality', 'food & beverages': 'travel, food & hospitality', 
    'restaurants': 'travel, food & hospitality', 'wine and spirits': 'travel, food & hospitality', 'gambling & casinos': 'travel, food & hospitality',
    'entertainment':'sports, media & entertainment', 'sports':'sports, media & entertainment', 'events services':'sports, media & entertainment', 
    'media production':'sports, media & entertainment', 'music':'sports, media & entertainment', 'online media':'sports, media & entertainment', 
    'sporting goods':'sports, media & entertainment', 'photography':'sports, media & entertainment', 'broadcast media':'sports, media & entertainment', 
    'graphic design':'sports, media & entertainment', 'computer games':'sports, media & entertainment', 'recreational facilities and services':'sports, media & entertainment', 
    'motion pictures and film':'sports, media & entertainment', 'animation':'sports, media & entertainment', 'newspapers':'sports, media & entertainment', 
    'public relations and communications':'sports, media & entertainment', 'fine art':'sports, media & entertainment', 'performing arts':'sports, media & entertainment', 
    'printing':'sports, media & entertainment', 'law practice': 'government, defense & legal', 'legal services': 'government, defense & legal', 
    'civic & social organization': 'government, defense & legal', 'security and investigations': 'government, defense & legal', 
    'government administration': 'government, defense & legal', 'religious institutions': 'government, defense & legal', 'defense & space': 'government, defense & legal', 
    'public policy': 'government, defense & legal', 'political organization': 'government, defense & legal', 'government relations': 'government, defense & legal', 
    'international affairs': 'government, defense & legal', 'law enforcement': 'government, defense & legal', 'judiciary': 'government, defense & legal', 
    'legislative office': 'government, defense & legal', 'military': 'government, defense & legal', 'alternative dispute resolution': 'government, defense & legal', 
    'executive office': 'government, defense & legal', 'retail': 'consumer & supply chain', 'apparel & fashion': 'consumer & supply chain', 
    'design': 'consumer & supply chain', 'consumer goods': 'consumer & supply chain', 'consumer services': 'consumer & supply chain', 'wholesale': 'consumer & supply chain', 
    'facilities services': 'consumer & supply chain', 'furniture': 'consumer & supply chain', 'food production': 'consumer & supply chain', 
    'business supplies and equipment': 'consumer & supply chain', 'logistics and supply chain': 'consumer & supply chain', 
    'individual & family services': 'consumer & supply chain', 'luxury goods & jewelry': 'consumer & supply chain', 'packaging and containers': 'consumer & supply chain', 
    'plastics': 'consumer & supply chain', 'package/freight delivery': 'consumer & supply chain', 'dairy': 'consumer & supply chain', 
    'supermarkets': 'consumer & supply chain', 'fishery': 'consumer & supply chain', 'international trade and development': 'consumer & supply chain', 
    'cosmetics': 'consumer & supply chain', 'farming': 'consumer & supply chain', 'textiles': 'consumer & supply chain', 'warehousing': 'consumer & supply chain', 
    'tobacco': 'consumer & supply chain', 'ranching': 'consumer & supply chain', 'transportation/trucking/railroad': 'consumer & supply chain',
    'maritime': 'consumer & supply chain', 'arts and crafts': 'consumer & supply chain'} 

    return output
