import csv
import io
import json

from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

SOIL_OPTIONS = {"黑土地", "河淤土", "沙土地", "红泥巴土", "黏泥巴"}
SEEDLING_STAGE_OPTIONS = {"发芽", "长根", "青麦", "授粉", "变黄", "逐渐成熟", "收割"}

CSV_FIELD_ALIASES = {
    "soil_type": "soil_type",
    "土壤": "soil_type",
    "soil": "soil_type",
    "seedling_stage": "seedling_stage",
    "生长周期": "seedling_stage",
    "seedling stage": "seedling_stage",
    "MOI": "MOI",
    "moi": "MOI",
    "种植密度": "MOI",
    "temp": "temp",
    "temperature": "temp",
    "温度": "temp",
    "humidity": "humidity",
    "湿度": "humidity",
}

CSV_REQUIRED_FIELDS = {"soil_type", "seedling_stage", "MOI", "temp", "humidity"}
CSV_MAX_ROWS = 2000


def _decode_csv_bytes(file_bytes):
    for encoding in ("utf-8-sig", "utf-8", "gbk", "gb2312"):
        try:
            return file_bytes.decode(encoding)
        except UnicodeDecodeError:
            continue
    raise ValueError("CSV 编码无法识别，请使用 UTF-8 或 GBK。")


def _normalize_field_name(field_name):
    key = (field_name or "").strip()
    if not key:
        return ""
    key_lower = key.lower()
    return CSV_FIELD_ALIASES.get(key) or CSV_FIELD_ALIASES.get(key_lower) or ""


def _normalize_csv_row(raw_row):
    normalized = {}
    for raw_key, raw_value in raw_row.items():
        canonical_key = _normalize_field_name(raw_key)
        if not canonical_key:
            continue
        normalized[canonical_key] = str(raw_value).strip() if raw_value is not None else ""
    return normalized


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


@require_http_methods(["POST"])
def predict_batch_api(request):
    if "login_user_id" not in request.session:
        return JsonResponse({"ok": False, "message": "登录状态已失效，请重新登录。"}, status=401)

    csv_file = request.FILES.get("csv_file")
    if csv_file is None:
        return JsonResponse({"ok": False, "message": "请上传 CSV 文件。"}, status=400)

    file_bytes = csv_file.read()
    if not file_bytes:
        return JsonResponse({"ok": False, "message": "CSV 文件内容为空。"}, status=400)

    try:
        csv_text = _decode_csv_bytes(file_bytes)
    except ValueError as exc:
        return JsonResponse({"ok": False, "message": str(exc)}, status=400)

    reader = csv.DictReader(io.StringIO(csv_text))
    if not reader.fieldnames:
        return JsonResponse({"ok": False, "message": "CSV 缺少表头。"}, status=400)

    valid_rows = []
    source_row_numbers = []
    errors = []

    for row_number, raw_row in enumerate(reader, start=2):
        if raw_row is None:
            continue
        if all((value is None or str(value).strip() == "") for value in raw_row.values()):
            continue

        row_data = _normalize_csv_row(raw_row)
        missing_fields = sorted(CSV_REQUIRED_FIELDS - set(row_data.keys()))
        if missing_fields:
            errors.append({"row": row_number, "message": f"缺少字段: {', '.join(missing_fields)}"})
            continue

        if row_data["soil_type"] not in SOIL_OPTIONS:
            errors.append({"row": row_number, "message": "soil_type 不在可选范围内。"})
            continue

        if row_data["seedling_stage"] not in SEEDLING_STAGE_OPTIONS:
            errors.append({"row": row_number, "message": "seedling_stage 不在可选范围内。"})
            continue

        try:
            float(row_data["MOI"])
            float(row_data["temp"])
            float(row_data["humidity"])
        except ValueError:
            errors.append({"row": row_number, "message": "MOI/temp/humidity 必须是 float 数值。"})
            continue

        valid_rows.append(
            {
                "soil_type": row_data["soil_type"],
                "seedling_stage": row_data["seedling_stage"],
                "MOI": row_data["MOI"],
                "temp": row_data["temp"],
                "humidity": row_data["humidity"],
            }
        )
        source_row_numbers.append(row_number)

        if len(valid_rows) > CSV_MAX_ROWS:
            return JsonResponse(
                {"ok": False, "message": f"单次最多处理 {CSV_MAX_ROWS} 条有效样本。"},
                status=400,
            )

    if not valid_rows:
        return JsonResponse(
            {
                "ok": False,
                "message": "没有可用于预测的数据，请检查 CSV 内容。",
                "errors": errors,
            },
            status=400,
        )

    try:
        from algorithm.predict import predict_from_request_for_batch

        predictions = predict_from_request_for_batch(valid_rows)
    except ImportError:
        return JsonResponse({"ok": False, "message": "预测依赖未安装（请检查 torch）。"}, status=500)
    except ValueError as exc:
        return JsonResponse({"ok": False, "message": str(exc)}, status=400)
    except Exception:
        return JsonResponse({"ok": False, "message": "批量预测服务异常，请稍后重试。"}, status=500)

    results = []
    need_irrigation_count = 0
    normal_count = 0
    for row_number, row_data, pred in zip(source_row_numbers, valid_rows, predictions):
        pred_int = int(pred)
        result_text = "需要灌溉" if pred_int == 1 else "一切正常"
        if pred_int == 1:
            need_irrigation_count += 1
        else:
            normal_count += 1

        results.append(
            {
                "row": row_number,
                "soil_type": row_data["soil_type"],
                "seedling_stage": row_data["seedling_stage"],
                "MOI": float(row_data["MOI"]),
                "temp": float(row_data["temp"]),
                "humidity": float(row_data["humidity"]),
                "result": pred_int,
                "result_text": result_text,
            }
        )

    summary = {
        "total_rows": len(source_row_numbers) + len(errors),
        "valid_rows": len(source_row_numbers),
        "error_rows": len(errors),
        "need_irrigation": need_irrigation_count,
        "normal": normal_count,
    }

    return JsonResponse(
        {
            "ok": True,
            "message": "批量预测完成。",
            "summary": summary,
            "results": results,
            "errors": errors,
        }
    )
