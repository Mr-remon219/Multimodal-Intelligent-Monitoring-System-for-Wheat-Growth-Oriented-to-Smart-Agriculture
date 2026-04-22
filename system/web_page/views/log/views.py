
from django.shortcuts import redirect, render

from ...models.users import User


def index(request):
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")

        if not username or not password:
            return render(
                request,
                "log/index.html",
                {
                    "error": "请输入用户名和密码。",
                    "username": username,
                },
                status=400,
            )

        user = User.objects.filter(user_name=username, password=password).first()
        if user is not None:
            request.session["login_user_id"] = user.id
            request.session["login_user_name"] = user.user_name
            return redirect("main_page")

        return render(
            request,
            "log/index.html",
            {
                "error": "用户名或密码错误，请重试。",
                "username": username,
            },
            status=401,
        )

    return render(request, "log/index.html")
