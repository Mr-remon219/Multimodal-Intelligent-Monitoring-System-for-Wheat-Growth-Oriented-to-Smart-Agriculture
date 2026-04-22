import json

from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods


@require_http_methods(["GET"])
def index(request):
    if "login_user_id" not in request.session:
        return redirect("log_index")
    return render(
        request,
        "main/page.html",
        {"login_user_name": request.session.get("login_user_name", "")},
    )


@require_http_methods(["POST"])
def predict_simple_api(request):
    if "login_user_id" not in request.session:
        return JsonResponse({"ok": False, "message": "登录状态已失效，请重新登录。"}, status=401)

    try:
        request_data = json.loads(request.body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return JsonResponse({"ok": False, "message": "请求体不是合法的 JSON。"}, status=400)

    required_fields = {"soil_type", "seedling_stage", "MOI", "temp", "humidity"}
    if not required_fields.issubset(request_data):
        return JsonResponse({"ok": False, "message": "参数不完整。"}, status=400)

    try:
        from algorithm.predict import predict_from_request_for_simple

        pred_result = int(predict_from_request_for_simple(request_data))
    except ImportError:
        return JsonResponse({"ok": False, "message": "预测依赖未安装（请检查 torch）。"}, status=500)
    except ValueError as exc:
        return JsonResponse({"ok": False, "message": str(exc)}, status=400)
    except Exception:
        return JsonResponse({"ok": False, "message": "预测服务异常，请稍后重试。"}, status=500)

    if pred_result == 1:
        return JsonResponse({"ok": True, "result": 1, "message": "需要灌溉"})
    return JsonResponse({"ok": True, "result": 0, "message": "一切正常"})
