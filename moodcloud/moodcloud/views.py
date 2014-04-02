# Create your views here.
from django.template import RequestContext
from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.core import serializers

from django.conf import settings

import urllib2
import json

import models

def index(request):
    return render(request, 'index.html', RequestContext(request))

# Get data from Whoooly
def fetch_data(request):
    data = urllib2.urlopen(settings.DATA_URL).read()
    json_data = json.loads(data)
    result = models.Result(search_term=json_data['globals'][1]['searchtext'])
    result.save()
    for t in json_data['topics']:
        topic_mood = models.Emotion.objects.get(label=t[1]['mood'])
        topic = models.Topic(topic=t[0]['topictext'], mood=topic_mood)
        topic.save()
        result.topics.add(topic)
    result.save()
    # Store the data in a model
    return HttpResponse()

# Return data to app/device
def get_data(request):
    result = models.Result.objects.latest()
    json_data = serializers.serialize('json', [result])
    jd = json.loads(json_data)[0]
    jd['fields']['topics'] = json.loads(serializers.serialize('json', result.topics.all()))
    moods = dict()
    for topic in result.topics.all():
        jmd = json.loads(serializers.serialize('json', [topic.mood]))[0]
        jd['fields']['topics'][topic.id-1]['fields']['mood'] = jmd
    return HttpResponse(json.dumps(jd), mimetype='application/json')

@csrf_exempt
def register(request):
    print request
    resp = HttpResponse("Ok")
    if request.POST:
        data = request.body.decode(encoding='UTF-8')
        jsondata = json.loads(data)
        addr = models.Address(network=jsondata['ip'])
        addr.save()
    return resp