from django.shortcuts import redirect
from django.views import generic

from ..models.users import User

def index(request):
    return redirect("log_index")

