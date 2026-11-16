import holidays, pandas as pd
ka = holidays.India(subdiv="KA", years=[2025])
pd.DataFrame(sorted(ka.items()), columns=["date", "holiday"]).to_csv("data/raw/holidays_karnataka_2025.csv", index=False)
ca = holidays.US(subdiv="CA", years=[2019])
pd.DataFrame(sorted(ca.items()), columns=["date", "holiday"]).to_csv("data/raw/holidays_california_2019.csv", index=False)
print(len(ka), len(ca))