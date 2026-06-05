import pandas as pd
import numpy as np
import os

np.random.seed(42)

n_rows = 200
dates = pd.date_range(start="2023-01-01", periods=n_rows)
regions = np.random.choice(["North America", "Europe", "Asia", "South America"], n_rows)

marketing_spend = np.random.uniform(500, 5000, n_rows)
new_users = (marketing_spend * np.random.uniform(0.05, 0.2, n_rows)).astype(int)
active_users = np.random.randint(1000, 10000, n_rows) + new_users
revenue = new_users * np.random.uniform(20, 100, n_rows) + active_users * np.random.uniform(1, 5, n_rows)
customer_satisfaction = np.clip(np.random.normal(4.2, 0.5, n_rows), 1, 5)

# Induce some missing values for realistic cleaning scenario
revenue[np.random.choice(n_rows, 10, replace=False)] = np.nan
customer_satisfaction[np.random.choice(n_rows, 5, replace=False)] = np.nan

df = pd.DataFrame({
    "Date": dates,
    "Region": regions,
    "Marketing_Spend": np.round(marketing_spend, 2),
    "New_Users": new_users,
    "Active_Users": active_users,
    "Revenue": np.round(revenue, 2),
    "Customer_Satisfaction": np.round(customer_satisfaction, 1)
})

os.makedirs("data", exist_ok=True)
df.to_csv("data/sample_data.csv", index=False)
print("sample_data.csv created successfully with 200 rows.")
