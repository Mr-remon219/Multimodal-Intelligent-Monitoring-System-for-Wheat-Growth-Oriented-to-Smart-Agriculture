from pathlib import Path

import torch

try:
    from .resnet18_for_1d.resnet181d import ResNet181D
except ImportError:
    from resnet18_for_1d.resnet181d import ResNet181D

SOIL_MAP = {
    "黑土地": 0,
    "河淤土": 1,
    "沙土地": 2,
    "红泥巴土": 3,
    "黏泥巴": 4,
}

SEEDLING_STAGE_MAP = {
    "发芽": 0,
    "长根": 1,
    "青麦": 2,
    "授粉": 3,
    "变黄": 4,
    "逐渐成熟": 5,
    "收割": 6,
}

_MODEL = None


def _load_model():
    global _MODEL
    if _MODEL is not None:
        return _MODEL

    model_path = Path(__file__).resolve().parent / "model.pth"
    model = ResNet181D(1, 2)
    state_dict = torch.load(model_path, map_location="cpu")
    model.load_state_dict(state_dict)
    model.eval()
    _MODEL = model
    return _MODEL


def predict_from_request_for_simple(request_data):
    try:
        soil_code = float(SOIL_MAP[request_data["soil_type"]])
        stage_code = float(SEEDLING_STAGE_MAP[request_data["seedling_stage"]])
        moi = float(request_data["MOI"])
        temp = float(request_data["temp"])
        humidity = float(request_data["humidity"])
    except KeyError as exc:
        raise ValueError(f"缺少或不支持的字段: {exc}") from exc
    except (TypeError, ValueError) as exc:
        raise ValueError("MOI、temp、humidity 必须是有效浮点数。") from exc

    feature = [0.0, soil_code, stage_code, moi, temp, humidity]
    x = torch.tensor(feature, dtype=torch.float32).unsqueeze(0).unsqueeze(1)
    model = _load_model()

    with torch.no_grad():
        output = model(x)
        pred = torch.argmax(output, dim=1)

    return int(pred.item())
