SOIL_OPTIONS = (
    "黑土地",
    "河淤土",
    "沙土地",
    "红泥巴土",
    "黏泥巴",
)

SEEDLING_STAGE_OPTIONS = (
    "发芽",
    "长根",
    "青麦",
    "授粉",
    "变黄",
    "逐渐成熟",
    "收割",
)

PREDICTION_FIELDS = (
    "soil_type",
    "seedling_stage",
    "MOI",
    "temp",
    "humidity",
)


def validate_prediction_payload(payload, strict_keys=False):
    if not isinstance(payload, dict):
        raise ValueError("请求体必须是 JSON 对象。")

    field_set = set(PREDICTION_FIELDS)
    payload_keys = set(payload.keys())

    if strict_keys:
        missing = sorted(field_set - payload_keys)
        extra = sorted(payload_keys - field_set)
        if missing or extra:
            messages = []
            if missing:
                messages.append(f"缺少字段: {', '.join(missing)}")
            if extra:
                messages.append(f"多余字段: {', '.join(extra)}")
            raise ValueError("；".join(messages))
    elif not field_set.issubset(payload_keys):
        missing = sorted(field_set - payload_keys)
        raise ValueError(f"缺少字段: {', '.join(missing)}")

    soil_type = str(payload.get("soil_type", "")).strip()
    seedling_stage = str(payload.get("seedling_stage", "")).strip()

    if soil_type not in SOIL_OPTIONS:
        raise ValueError("soil_type 不在可选范围内。")
    if seedling_stage not in SEEDLING_STAGE_OPTIONS:
        raise ValueError("seedling_stage 不在可选范围内。")

    try:
        moi = float(payload.get("MOI"))
        temp = float(payload.get("temp"))
        humidity = float(payload.get("humidity"))
    except (TypeError, ValueError) as exc:
        raise ValueError("MOI、temp、humidity 必须是 float 数值。") from exc

    return {
        "soil_type": soil_type,
        "seedling_stage": seedling_stage,
        "MOI": moi,
        "temp": temp,
        "humidity": humidity,
    }
