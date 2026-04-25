import json

from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

from ...models.sensor_storage import insert_user_sensor_record
from ...models.users import User
from ...prediction_schema import validate_prediction_payload


@require_http_methods(["POST"])
def upload_by_sensor_key(request, sensor_key):
    user = User.objects.filter(sensor_key=sensor_key).first()
    if user is None:
        return JsonResponse({"ok": False, "message": "无效的传感器密钥。"}, status=404)

    try:
        payload = json.loads(request.body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return JsonResponse({"ok": False, "message": "请求体不是合法 JSON。"}, status=400)

    try:
        normalized_payload = validate_prediction_payload(payload, strict_keys=True)
    except ValueError as exc:
        return JsonResponse({"ok": False, "message": str(exc)}, status=400)

    try:
        table_name, row_id = insert_user_sensor_record(user.id, normalized_payload)
    except Exception:
        return JsonResponse({"ok": False, "message": "数据写入失败，请稍后重试。"}, status=500)

    return JsonResponse(
        {
            "ok": True,
            "message": "上传成功。",
            "table_name": table_name,
            "record_id": row_id,
            "uploaded_data": normalized_payload,
        },
        status=201,
    )
