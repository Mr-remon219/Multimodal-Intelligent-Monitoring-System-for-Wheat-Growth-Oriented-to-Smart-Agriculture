
import json

from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods
from ...models.users import User
from ...sensor_storage import ensure_user_sensor_table


@require_http_methods(["GET", "POST"])
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


@require_http_methods(["GET"])
def register_page(request):
    return render(request, "log/register.html")


@require_http_methods(["POST"])
def register_api(request):
    try:
        payload = json.loads(request.body.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse(
            {"ok": False, "message": "请求格式错误，请重试。"},
            status=400,
        )

    username = str(payload.get("username", "")).strip()
    password = str(payload.get("password", ""))
    confirm_password = str(payload.get("confirm_password", ""))

    if not username or not password or not confirm_password:
        return JsonResponse(
            {"ok": False, "message": "请完整填写用户名和密码。"},
            status=400,
        )

    if len(username) > 20 or len(password) > 20:
        return JsonResponse(
            {"ok": False, "message": "用户名和密码长度不能超过 20。"},
            status=400,
        )

    if password != confirm_password:
        return JsonResponse(
            {"ok": False, "message": "两次输入的密码不一致。"},
            status=400,
        )

    if User.objects.filter(user_name=username).exists():
        return JsonResponse(
            {"ok": False, "message": "用户名已存在，请更换后再试。"},
            status=409,
        )

    try:
        with transaction.atomic():
            user = User.objects.create(user_name=username, password=password)
            ensure_user_sensor_table(user.id)
    except Exception:
        return JsonResponse(
            {"ok": False, "message": "注册失败，请稍后重试。"},
            status=500,
        )

    return JsonResponse({"ok": True, "message": "注册成功，即将跳转登录页。"})
