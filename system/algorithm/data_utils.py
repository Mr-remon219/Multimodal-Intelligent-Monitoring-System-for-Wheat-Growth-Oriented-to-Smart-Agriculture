import pandas as pd
import torch
from torch.utils.data import Dataset, DataLoader
import numpy as np

file_path = r"cropdata_updated.csv"

class WheatDataset(Dataset):
    def __init__(self):
        super().__init__()
        self.file = pd.read_csv(file_path)
        self.feature = self.file.iloc[:, 3 : -1].to_numpy(dtype=np.float32)
        self.label = self.file.iloc[:,  -1].to_numpy(dtype=np.long)

    def __len__(self):
        return len(self.feature)

    def __getitem__(self, idx):
        x = torch.tensor(self.feature[idx], dtype=torch.float32)
        y = torch.tensor(self.label[idx], dtype=torch.long)

        return x, y

if __name__ == "__main__":
    dataset = WheatDataset()
    loader = DataLoader(dataset, batch_size=64, shuffle=True)
    for x, y in loader:
        print(x)
        print(y)
        break
