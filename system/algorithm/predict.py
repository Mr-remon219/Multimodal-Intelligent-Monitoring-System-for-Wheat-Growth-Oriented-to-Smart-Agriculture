from resnet18_for_1d.resnet181d import ResNet181D
import torch 
import pandas as pd

soil_dict = {"黑土地": 0, "河淤土": 1, "沙土地": 2, "红泥巴土": 3, "黏泥巴": 4}
seedling_stage_dict = {"发芽": 0, "长根": 1, "青麦": 2, "授粉": 3, "变黄": 4, "逐渐成熟": 5, "收割": 6}

def predict_from_request_for_simple(request_data):
    feature = [
        float(0),
        float(soil_dict[request_data["soil_type"]]),
        float(seedling_stage_dict[request_data["seedling_stage"]]),
        float(request_data["MOI"]),
        float(request_data["temp"]),
        float(request_data["humidity"])
    ]

    x = torch.tensor(feature, dtype=torch.float32)

    model = ResNet181D(1, 2)
    model.load_state_dict(torch.load("model.pth", map_location='cpu'))
    model.eval()

    x = x.unsqueeze(0)
    x = x.unsqueeze(1)
    
    with torch.no_grad():
        output = model(x)
        pred = torch.argmax(output, dim=1)
    
    return pred[0]