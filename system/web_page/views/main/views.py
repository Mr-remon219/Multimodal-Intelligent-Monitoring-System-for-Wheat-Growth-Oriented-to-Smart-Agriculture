from django.shortcuts import redirect, render


def index(request):
    if "login_user_id" not in request.session:
        return redirect("log_index")
    return render(
        request,
        "main/page.html",
        {"login_user_name": request.session.get("login_user_name", "")},
    )
