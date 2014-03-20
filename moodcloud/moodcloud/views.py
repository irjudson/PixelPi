# Create your views here.
from django.template import RequestContext
from django.shortcuts import render

def index(request):
    return render(request, 'index.html', RequestContext(request))
