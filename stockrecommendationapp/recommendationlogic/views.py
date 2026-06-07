from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.



def recommendation_view(request):
    return HttpResponse("<h1>Page was found for recommendation</h1>")