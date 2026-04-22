from django.shortcuts import render
from django.db.models import F
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic

from ..models.users import User

def index(request):
    return render(request, "main/page.html")

class TestView(generic.DetailView):
    model = User
    template_name = "web_page/test.html"
