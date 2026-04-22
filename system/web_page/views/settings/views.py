from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from ...models.users import User, generate_sensor_key
from ...prediction_schema import PREDICTION_FIELDS, SEEDLING_STAGE_OPTIONS, SOIL_OPTIONS
from ...sensor_storage import ensure_user_sensor_table


@require_http_methods(["GET", "POST"])
def index(request):
    login_user_id = request.session.get("login_user_id")
    if not login_user_id:
        return redirect("log_index")

    user = User.objects.filter(id=login_user_id).first()
    if user is None:
        request.session.flush()
        return redirect("log_index")

    if not user.sensor_key:
        while True:
            candidate = generate_sensor_key()
            if not User.objects.filter(sensor_key=candidate).exists():
                user.sensor_key = candidate
                user.save(update_fields=["sensor_key"])
                break

    ensure_user_sensor_table(user.id)

    message = ""
    message_type = ""

    if request.method == "POST":
        action = request.POST.get("action", "").strip()

        if action == "update_username":
            new_username = request.POST.get("new_username", "").strip()
            current_password = request.POST.get("current_password", "")

            if not new_username or not current_password:
                message = "请完整填写修改用户名所需字段。"
                message_type = "error"
            elif len(new_username) > 20:
                message = "用户名长度不能超过 20。"
                message_type = "error"
            elif current_password != user.password:
                message = "当前密码错误，无法修改用户名。"
                message_type = "error"
            elif User.objects.filter(user_name=new_username).exclude(id=user.id).exists():
                message = "该用户名已被占用，请更换。"
                message_type = "error"
            else:
                user.user_name = new_username
                user.save(update_fields=["user_name"])
                request.session["login_user_name"] = user.user_name
                message = "用户名修改成功。"
                message_type = "success"

        elif action == "update_password":
            old_password = request.POST.get("old_password", "")
            new_password = request.POST.get("new_password", "")
            confirm_password = request.POST.get("confirm_password", "")

            if not old_password or not new_password or not confirm_password:
                message = "请完整填写修改密码所需字段。"
                message_type = "error"
            elif old_password != user.password:
                message = "旧密码错误。"
                message_type = "error"
            elif len(new_password) > 20:
                message = "新密码长度不能超过 20。"
                message_type = "error"
            elif new_password != confirm_password:
                message = "两次输入的新密码不一致。"
                message_type = "error"
            else:
                user.password = new_password
                user.save(update_fields=["password"])
                message = "密码修改成功。"
                message_type = "success"
        else:
            message = "无效操作。"
            message_type = "error"

    return render(
        request,
        "settings/index.html",
        {
            "login_user_name": request.session.get("login_user_name", ""),
            "sensor_key": user.sensor_key,
            "sensor_upload_path": f"/sensor/{user.sensor_key}/upload/",
            "prediction_fields": PREDICTION_FIELDS,
            "soil_options": SOIL_OPTIONS,
            "seedling_stage_options": SEEDLING_STAGE_OPTIONS,
            "message": message,
            "message_type": message_type,
        },
    )
