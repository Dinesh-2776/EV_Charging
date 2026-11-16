import os
import ast
import pandas as pd
import matplotlib.pyplot as plt

os.makedirs("figures", exist_ok=True)
df = pd.read_csv("data/raw/caltech_2019.csv")

# 1. Parse times and convert to California local time
for c in ["connectionTime", "disconnectTime", "doneChargingTime"]:
    df[c] = pd.to_datetime(df[c], utc=True, errors="coerce").dt.tz_convert("America/Los_Angeles")

print("Rows:", len(df))
print("Missing values:\n", df[["connectionTime", "disconnectTime", "doneChargingTime", "kWhDelivered"]].isna().sum())

# 2. How many sessions have userInputs, and what is inside?
def parse(x):
    if pd.isna(x) or x == "":
        return None
    try:
        return ast.literal_eval(x)
    except Exception:
        return "PARSE_FAILED"

df["ui"] = df["userInputs"].apply(parse)
has = df["ui"].apply(lambda v: bool(v) and v != "PARSE_FAILED")
failed = (df["ui"] == "PARSE_FAILED").sum()
print(f"\nSessions with userInputs: {has.sum()} of {len(df)} ({has.mean()*100:.1f}%)")
print("Parse failures:", failed)
if has.sum() > 0:
    print("Fields inside userInputs:", list(df.loc[has, "ui"].iloc[0][0].keys()))
else:
    print("Raw sample:", df["userInputs"].dropna().iloc[0][:500])

# 3. Durations in hours
df["stay_h"] = (df.disconnectTime - df.connectionTime).dt.total_seconds() / 3600
df["charge_h"] = (df.doneChargingTime - df.connectionTime).dt.total_seconds() / 3600
df["overstay_h"] = df.stay_h - df.charge_h
print("\n", df[["kWhDelivered", "stay_h", "charge_h", "overstay_h"]].describe())

# 4. Plot: arrivals by hour, weekday vs weekend
df["hour"] = df.connectionTime.dt.hour
df["weekend"] = df.connectionTime.dt.dayofweek >= 5
counts = df.groupby(["hour", "weekend"]).size().unstack(fill_value=0)
counts.columns = ["Weekday" if not c else "Weekend" for c in counts.columns]
counts.plot(kind="bar", figsize=(10, 4), title="Arrivals by hour (Caltech 2019)")
plt.xlabel("Hour of day")
plt.ylabel("Number of sessions")
plt.tight_layout()
plt.savefig("figures/arrivals_by_hour.png")

# 5. Plot: stay vs charging time
plt.figure(figsize=(6, 4))
df["stay_h"].clip(upper=24).plot(kind="hist", bins=48, alpha=0.6, label="Stay (plugged in)")
df["charge_h"].clip(upper=24).plot(kind="hist", bins=48, alpha=0.6, label="Charging")
plt.legend()
plt.xlabel("Hours")
plt.title("Plugged-in time vs charging time")
plt.tight_layout()
plt.savefig("figures/stay_vs_charge.png")
print("\nPlots saved in the figures folder.")