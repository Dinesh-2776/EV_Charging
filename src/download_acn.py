from acnportal import acndata
from datetime import datetime
import pandas as pd

with open("token.txt") as f:
    token = f.read().strip()

client = acndata.DataClient(token)

site = "caltech"   # change to "jpl" for the second site
start = datetime(2019, 1, 1)
end = datetime(2019, 12, 31)

sessions = client.get_sessions_by_time(site, start, end)
df = pd.DataFrame(list(sessions))

print("Rows:", df.shape[0])
print("Columns:", list(df.columns))
print(df.head())

df.to_csv(f"data/raw/{site}_2019.csv", index=False)
print("Saved.")