import re
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, render
from django.template import loader

from .models import QuestionAnswer

# Create your views here.


def index(req):
    latest_qs = QuestionAnswer.objects.all()
    context = {"latest_qs": latest_qs}

    return render(req, "seapanapp/index.html", context)


def q_details(req, question_id):
    q = get_object_or_404(QuestionAnswer, pk=question_id)
    return render(req, "seapanapp/q_detail.html", {"q": q})


def search(req):
    return render(req, "seapanapp/search.html")


def searchres(req):
    query = req.POST["query"]
    # TODO: NLP stuff
    results = QuestionAnswer.objects.all()

    return render(req, "seapanapp/searchres.html", {"query": query, "results": results})
