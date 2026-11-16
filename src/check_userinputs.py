import re, collections
import pandas as pd

df = pd.read_csv("data/raw/caltech_2019.csv")
s = df["userInputs"].fillna("")
has = s.str.len() > 2
print("Sessions:", len(df), " with userInputs:", int(has.sum()), f"({has.mean()*100:.1f}%)")

cnt = collections.Counter()
for x in s[has]:
    cnt.update(set(re.findall(r"'(\w+)':", x)))
print("\nField name : number of sessions that have it")
for k, v in cnt.most_common():
    print(f"{k:22s} {v}")

print("\nExample:", s[has].iloc[0][:600])