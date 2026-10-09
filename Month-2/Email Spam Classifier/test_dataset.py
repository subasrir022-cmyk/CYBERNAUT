
from pathlib import Path

data_path = Path("data/SMSSpamCollection")

if data_path.exists():
    print("Dataset found successfully!")

    with open(data_path, "r", encoding="utf-8") as file:
        for i in range(5):
            print(file.readline().strip())
else:
    print("Dataset not found!")
    print("Please check the data folder and file name.")