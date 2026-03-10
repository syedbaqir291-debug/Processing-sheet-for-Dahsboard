# preprocess_oncology_metrics.py

import pandas as pd
import numpy as np

# -------------------------
# 1️⃣ Load raw Excel
# -------------------------
file_path = "raw_oncology_data.xlsx"  # change this to your file
df = pd.read_excel(file_path)

cancer_col = "Cancer Category"
month_col = "Month"

# List of metrics to compute stats on
metric_cols = [
    "1st visit - WIC acceptance",
    "WIC acceptance - 1st OPD visit",
    "1st OPD visit - MDT",
    "MDT - 1st day of treatment",
    "Number of days"
]

# -------------------------
# 2️⃣ Robust numeric cleaning
# -------------------------
for col in metric_cols:
    df[col] = df[col].astype(str).str.strip()                     # remove spaces
    df[col] = df[col].str.replace(r'[^\d.]', '', regex=True)     # remove non-numeric chars
    df[col] = pd.to_numeric(df[col], errors='coerce')            # convert to numeric

# -------------------------
# 3️⃣ Aggregate per Cancer Category + Month
# -------------------------
agg_funcs = {
    "Mean": np.nanmean,
    "Median": np.nanmedian,
    "SD": lambda x: np.nanstd(x, ddof=1),
    "Max": np.nanmax,
    "Min": np.nanmin
}

result_rows = []

for metric in metric_cols:
    grouped = df.groupby([cancer_col, month_col])[metric].agg(agg_funcs).reset_index()
    
    # Rename columns to include metric name
    grouped = grouped.rename(columns={
        "Mean": f"Mean of {metric}",
        "Median": f"Median of {metric}",
        "SD": f"SD of {metric}",
        "Max": f"Max of {metric}",
        "Min": f"Min of {metric}"
    })
    
    result_rows.append(grouped)

# -------------------------
# 4️⃣ Merge all metrics into a single DataFrame
# -------------------------
from functools import reduce

processed_df = reduce(lambda left, right: pd.merge(left, right, on=[cancer_col, month_col]), result_rows)

# Round numeric columns
numeric_cols = [col for col in processed_df.columns if col not in [cancer_col, month_col]]
processed_df[numeric_cols] = processed_df[numeric_cols].round(2)

# -------------------------
# 5️⃣ Save processed sheet
# -------------------------
processed_file = "processed_oncology_metrics.xlsx"
processed_df.to_excel(processed_file, index=False)
print(f"Processed file saved as '{processed_file}'")
