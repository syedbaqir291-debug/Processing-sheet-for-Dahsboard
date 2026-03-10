# app_cancer_stats_dashboard.py

import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="Cancer Metrics Dashboard", layout="wide")
st.title("Cancer Metrics Aggregation Dashboard")

# 1. Upload Excel file
uploaded_file = st.file_uploader("Upload Excel file", type=["xlsx", "xls"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    st.success("File loaded successfully!")
    st.dataframe(df.head(5))

    # 2. Select columns
    month_col = st.selectbox("Select the Month column", df.columns)
    cancer_col = st.selectbox("Select the Cancer Category column", df.columns)
    
    # Parameter selection (up to 5)
    parameter_cols = st.multiselect(
        "Select up to 5 parameters",
        df.columns,
        default=df.columns[:5]
    )

    if len(parameter_cols) > 5:
        st.warning("Please select no more than 5 parameters.")
    
    elif len(parameter_cols) > 0:
        # 3. Create aggregation functions
        agg_funcs = {
            "Mean": "mean",
            "Median": "median",
            "Standard Deviation": "std",
            "Maximum": "max",
            "Minimum": "min"
        }

        # 4. Create a BytesIO object to save Excel
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            for stat_name, func in agg_funcs.items():
                # Group by Cancer Category
                grouped = df.groupby(cancer_col)[parameter_cols].agg(func).reset_index()
                grouped.to_excel(writer, sheet_name=stat_name, index=False)
        
        # 5. Provide download
        st.download_button(
            label="Download Aggregated Excel",
            data=output.getvalue(),
            file_name="cancer_category_metrics.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
