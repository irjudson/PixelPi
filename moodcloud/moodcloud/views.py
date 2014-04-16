# Create your views here.
from django.template import RequestContext
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.core import serializers
from django.utils.timezone import utc
from django.conf import settings

import urllib
import urllib2
import json
import datetime
import traceback

from twitter import *

import pytz
import models

def make_result_from_json(json_data):
    if 'searchtext' in json_data['globals'][1]:
        result = models.Result(search_term=json_data['globals'][1]['searchtext'])
        result.save()
        for t in json_data['topics']:
            topic_mood = models.Emotion.objects.get(label=t[1]['mood'])
            topic = models.Topic(topic=t[0]['topictext'], mood=topic_mood)
            topic.save()
            result.topics.add(topic)
        result.save()
        return result
    else:
        print "Didn't find searchtext in globals"
        return None

def fetch():
    result = make_result_from_json(json.loads(urllib2.urlopen(settings.DATA_URL).read()))
    return result

def do_search(search_term):
    server_url = "http://whooly.cloudapp.net/api/MoodCloud?term=%s" % urllib.quote_plus(search_term)

    request = urllib2.Request(server_url)
    response = urllib2.urlopen(request)
    data = response.read()
    jd = json.loads(data)
    if jd['topics'] is None:
        print "failed! (to get search results)"
        return None
    result = make_result_from_json(json.loads(data))
    return result

def home(request):
    context = RequestContext(request)
    #twitter = Twitter(auth=OAuth(settings.OAUTH_TOKEN, settings.OAUTH_SECRET,
    #                             settings.CONSUMER_KEY, settings.CONSUMER_SECRET))
    #trends = twitter.trends._woeid(_woeid = 1)
    #print trends['results']
    context['trends'] = None
    terms = list()
    count = 0
    for x in models.Result.objects.all():
         if x.search_term.lower() not in terms:
             terms.append(x.search_term.lower())
             count += 1
         if count > 5:
             break
    context['recent'] = [x.capitalize() for x in terms]
    return render(request, 'home.html', context)

@csrf_exempt
def search(request, search_term):
    if not search_term and 'search_term' in request.GET:
        search_term = request.GET['search_term']
    if not search_term and 'search' in request.POST:
        search_term = request.POST['search']
    if not search_term:
        return HttpResponseBadRequest()
    context = RequestContext(request)
    context['Result'] = do_search(search_term)
    context['IP'] = models.Address.load().network or "Unknown"
    context['IP_updated'] = models.Address.load().last_updated or "Never updated"
    return render(request, 'search_results.html', context)

# Get data from Whoooly
def fetch_data(request):
    # Get Data
    fetch()
    # Store the data in a model
    return HttpResponse()

# Return data to app/device
def get_data(request):
    result = None
    try:
        diff =  pytz.utc.localize( datetime.datetime.utcnow() ) - models.Result.objects.latest().created_at
        if models.Result.objects.count() == 0:
            result = fetch()
        if diff.seconds > settings.UPDATE_FREQUENCY:
            result = fetch()
        if result == None:
            result = models.Result.objects.latest()
        json_data = serializers.serialize('json', [result])
        jd = json.loads(json_data)[0]
        jd['fields']['topics'] = json.loads(serializers.serialize('json', result.topics.all()))
        moods = dict()
        count = 0
        for topic in result.topics.all():
            jmd = json.loads(serializers.serialize('json', [topic.mood]))[0]
            jd['fields']['topics'][count]['fields']['mood'] = jmd
            count += 1
    except Exception as e:
        print "Exception: %s" % e.message
        traceback.print_exc()
        jd = {}
    return HttpResponse(json.dumps(jd), content_type='application/json')

@csrf_exempt
def register(request):
    resp = HttpResponse("Ok")
    if request.POST:
        data = request.body.decode(encoding='UTF-8')
        jsondata = json.loads(data)
        addr = models.Address(network=jsondata['ip'])
        addr.save()
    return resp