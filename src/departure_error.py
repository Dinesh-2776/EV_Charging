import os, ast
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

os.makedirs("figures", exist_ok=True)
df = pd.read_csv("data/raw/caltech_2019.csv")
for c in ["connectionTime", "disconnectTime", "doneChargingTime"]:
    df[c] = pd.to_datetime(df[c], utc=True, errors="coerce")

def last_and_first(x):
    if not isinstance(x, str) or len(x) < 3:
        return None, None
    try:
        lst = ast.literal_eval(x)
    except Exception:
        return None, None
    lst = [e for e in lst if isinstance(e, dict) and e.get("requestedDeparture")]
    if not lst:
        return None, None
    lst.sort(key=lambda e: pd.to_datetime(e.get("modifiedAt"), utc=True, errors="coerce"))
    return lst[0], lst[-1]

fl = df["userInputs"].apply(last_and_first)
df["first"] = fl.apply(lambda t: t[0])
df["last"] = fl.apply(lambda t: t[1])
d = df[df["last"].notna()].copy()
d["req_final"] = pd.to_datetime(d["last"].apply(lambda e: e["requestedDeparture"]), utc=True, errors="coerce")
d["req_first"] = pd.to_datetime(d["first"].apply(lambda e: e["requestedDeparture"]), utc=True, errors="coerce")
d["kwh_req"] = d["last"].apply(lambda e: e.get("kWhRequested"))
d["user"] = d["last"].apply(lambda e: e.get("userID"))
d["n_edits"] = d["userInputs"].apply(lambda x: len(ast.literal_eval(x)))

d["err_final"] = (d["disconnectTime"] - d["req_final"]).dt.total_seconds() / 60
d["err_first"] = (d["disconnectTime"] - d["req_first"]).dt.total_seconds() / 60
d = d.dropna(subset=["err_final"])
a = d["err_final"].abs()

print("Sessions with a declared departure:", len(d), " unique users:", d["user"].nunique())
print("Sessions where the driver edited the request (more than 1 entry):", int((d["n_edits"] > 1).sum()))
print("\n--- Final declared departure vs actual unplug (minutes, negative = left early) ---")
print(d["err_final"].describe().round(1))
print(f"Median absolute error: {a.median():.1f} min   Mean absolute error: {a.mean():.1f} min")
print(f"Within +-15 min: {(a<=15).mean()*100:.1f}%   Within +-60 min: {(a<=60).mean()*100:.1f}%")
print(f"Left more than 15 min EARLY: {(d['err_final']<-15).mean()*100:.1f}%   More than 15 min LATE: {(d['err_final']>15).mean()*100:.1f}%")
print(f"First-entry mean abs error: {d['err_first'].abs().mean():.1f} min (vs final {a.mean():.1f})")

d["energy_ratio"] = d["kWhDelivered"] / d["kwh_req"].replace(0, np.nan)
er = d["energy_ratio"].replace([np.inf, -np.inf], np.nan).dropna()
print(f"\nEnergy delivered / requested: median {er.median():.2f}; sessions delivering < 80% of request: {(er<0.8).mean()*100:.1f}%")

# Does a driver's PAST accuracy predict their NEXT accuracy? (premise of the trust score)
d = d.sort_values(["user", "connectionTime"])
d["abs_err"] = d["err_final"].abs()
d["prior_mae"] = d.groupby("user")["abs_err"].transform(lambda s: s.shift().expanding().mean())
d["n_prior"] = d.groupby("user").cumcount()
t = d[d["n_prior"] >= 3].dropna(subset=["prior_mae"])
print(f"\n--- Trust-score test: sessions with at least 3 earlier sessions by the same driver: {len(t)} ---")
if len(t) > 50:
    rho = t["prior_mae"].rank().corr(t["abs_err"].rank())
    print(f"Rank correlation (past mean error vs current error): {rho:.2f}")
    t = t.assign(group=pd.qcut(t["prior_mae"], 3, labels=["Most reliable", "Middle", "Least reliable"]))
    print(t.groupby("group", observed=True)["abs_err"].agg(["count", "mean", "median"]).round(1))

plt.figure(figsize=(7, 4))
d["err_final"].clip(-240, 240).plot(kind="hist", bins=96)
plt.axvline(0, color="k", lw=1)
plt.xlabel("Actual unplug minus declared departure (minutes; negative = left early)")
plt.ylabel("Sessions"); plt.title("Declared vs actual departure (Caltech 2019)")
plt.tight_layout(); plt.savefig("figures/departure_error.png", dpi=150)
print("\nSaved figures/departure_error.png")