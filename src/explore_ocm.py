import os
import pandas as pd
import matplotlib.pyplot as plt

os.makedirs("figures", exist_ok=True)
os.makedirs("data/clean", exist_ok=True)

df = pd.read_csv("data/raw/ocm_bengaluru.csv")
print("Rows:", len(df), " Unique ids:", df["id"].nunique())

# Clean
df = df.drop_duplicates("id").dropna(subset=["lat", "lon"])
df["town"] = df["town"].fillna("Unknown").str.strip().str.title().replace({"Bangalore": "Bengaluru"})
df["operator"] = df["operator"].fillna("Unknown")

# Power buckets
bins = [0, 7.5, 25, 60.5, 1000]
labels = ["Slow (<=7.4 kW)", "Medium AC/DC (22-25 kW)", "DC fast (30-60 kW)", "High power (>60 kW)"]
df["power_bucket"] = pd.cut(df["max_power_kw"], bins=bins, labels=labels)

print("\nMissing power:", df["max_power_kw"].isna().sum())
print("\nTown:\n", df["town"].value_counts().head(8))
print("\nTop operators:\n", df["operator"].value_counts().head(10))
print("\nPower buckets:\n", df["power_bucket"].value_counts(dropna=False))
print("\nTotal charging points:", int(df["points"].fillna(1).sum()))

df.to_csv("data/clean/ocm_bengaluru_clean.csv", index=False)

# Map-style scatter
plt.figure(figsize=(7, 7))
for lab, g in df.groupby("power_bucket", observed=True):
    plt.scatter(g["lon"], g["lat"], s=18, label=lab, alpha=0.8)
plt.legend(fontsize=8)
plt.xlabel("Longitude"); plt.ylabel("Latitude")
plt.title("Charging stations around Bengaluru (Open Charge Map)")
plt.tight_layout()
plt.savefig("figures/ocm_map.png", dpi=150)
print("Saved figures/ocm_map.png")