
import pandas as pd

# Load the dataset
df = pd.read_csv(
    "data/SMSSpamCollection",
    sep="\t",
    header=None,
    names=["label", "message"],
    encoding="utf-8"
)

print("\nFIRST 5 MESSAGES:")
print(df.head())

print("\nTOTAL MESSAGES:")
print(len(df))

print("\nSPAM AND HAM COUNTS:")
print(df["label"].value_counts())

print("\nMISSING VALUES:")
print(df.isnull().sum())