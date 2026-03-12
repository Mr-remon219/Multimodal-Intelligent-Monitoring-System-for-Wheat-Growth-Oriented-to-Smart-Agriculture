import torch
import torch.nn as nn
from torch import Tensor


def conv3x3(in_planes: int, out_planes:int, stride: int = 1) -> nn.Conv2d:
    return nn.Conv2d(in_planes, out_planes, kernel_size=3, stride=stride, padding=1, bias=False)

def conv1x1(in_planes: int, out_planes: int, stride: int = 1) -> nn.Conv2d:
    return nn.Conv2d(in_planes, out_planes, kernel_size=1, stride=stride, padding=0, bias=False)

def conv7x7(in_planes: int, out_planes: int, stride: int = 1) -> nn.Conv2d:
    return nn.Conv2d(in_planes, out_planes, kernel_size=7, stride=stride, padding=3, bias=False)

class BasicBlock(nn.Module):

    def __init__(self, in_planes: int, out_planes: int, stride: int = 1, process: bool = False) -> None:
        super().__init__()
        self.conv1 = conv3x3(in_planes, out_planes, stride)
        self.bn1 = nn.BatchNorm2d(out_planes)
        self.relu = nn.ReLU(inplace=True)
        self.conv2 = conv3x3(out_planes, out_planes)
        self.bn2 = nn.BatchNorm2d(out_planes)
        self.stride = stride
        self.process = process
        self.convex = conv1x1(in_planes, out_planes, stride)

    def forward(self, x: Tensor) -> Tensor:
        identity = x

        out = self.conv1(x)
        out = self.bn1(out)
        out = self.relu(out)

        out = self.conv2(out)
        out = self.bn2(out)

        if self.process:
            identity = self.convex(identity)

        out += identity
        out = self.relu(out)

        return out

class ResNet18(nn.Module):
    def __init__(self, in_planes: int, num_classes: int) -> None:
        super().__init__()
        self.in_planes = in_planes
        self.conv1 = conv7x7(self.in_planes, 64, 3)
        self.bn1 = nn.BatchNorm2d(64)
        self.maxpool = nn.MaxPool2d(kernel_size=3, stride=2, padding=1)
        self.layer1 = self._make_layer(64, 64)
        self.layer2 = self._make_layer(64, 128, stride=2)
        self.layer3 = self._make_layer(128, 256, stride=2, process=True)
        self.layer4 = self._make_layer(256, 512, stride=2)
        self.avgpool = nn.AvgPool2d((1, 1))
        self.fc = nn.Linear(512, num_classes)





    def _make_layer(self, in_planes: int, out_planes: int, stride: int = 1, process: bool = False) -> nn.Sequential:
        layers = []
        layers.append(BasicBlock(in_planes, out_planes, stride, process=process))
        layers.append(BasicBlock(out_planes, out_planes, stride, process=process))

        return nn.Sequential(*layers)

    def forward(self, x: Tensor) -> Tensor:
        x = self.conv1(x)
        x = self.bn1(x)
        x = self.maxpool(x)

        x = self.layer1(x)
        x = self.layer2(x)
        x = self.layer3(x)
        x = self.layer4(x)

        x = self.avgpool(x)
        x = torch.flatten(x, 1)
        x = self.fc(x)

        return x
