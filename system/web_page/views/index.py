from django.shortcuts import redirect
from django.views import generic

from ..models.users import User

def index(request):
    return redirect("log_index")

class TestView(generic.DetailView):
    model = User
    template_name = "web_page/test.html"
