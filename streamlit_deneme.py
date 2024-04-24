#!/usr/bin/env python
# coding: utf-8

import streamlit as st
import pandas as pd
from datetime import datetime,date,timedelta
from retrying import retry
import requests
import os

# Function to fetch data (mock function)
@retry(stop_max_attempt_number=5)
def PTF_SMF(start,end):
    url = "https://seffaflik.epias.com.tr/electricity-service"
    endpoint_ptf = "/v1/markets/dam/data/mcp"
    endpoint_smf = "/v1/markets/bpm/data/system-marginal-price"

    param = {"startDate" : start, "endDate": end}

    ptf = requests.post(url+endpoint_ptf, json = param)
    ptf_df = pd.DataFrame(ptf.json()["items"]).set_index("date")
    ptf_df.index = pd.to_datetime(ptf_df.index)

    smf = requests.post(url+endpoint_smf, json = param)
    smf_df = pd.DataFrame(smf.json()["items"]).set_index("date")
    smf_df.index = pd.to_datetime(smf_df.index)

    ptf_smf = pd.DataFrame(index = pd.date_range(start,end,freq="h"))
    ptf_smf["PTF"] = ptf_df["price"]
    ptf_smf["SMF"] = smf_df["systemMarginalPrice"]
    ptf_smf.index = ptf_smf.index.strftime("%Y-%m-%d %H:%M:%S")
    
    return ptf_smf
st.title('PTF-SMF')


start_date = datetime(datetime.today().year, 1, 1).date()  # year start
end_date = datetime.today().date()  # today

selected_start_date, selected_end_date= st.slider(
    "Select Date Range",
    min_value=start_date,
    max_value=end_date,
    value=(end_date-timedelta(days=1), end_date-timedelta(days=1)),
    #format="DD/MM/YYYY"  # You can change the display format here if needed
)

selected_start_date = selected_start_date.strftime("%Y-%m-%dT00:00:00+03:00")
selected_end_date = selected_end_date.strftime("%Y-%m-%dT23:00:00+03:00")

# Load data using the function
data = PTF_SMF(selected_start_date,selected_end_date)

# Display the dataframe in the app
st.write("Here is our data:")
st.dataframe(data)  

if st.button('Download as Excel'):
    st.write("Downloading data as Excel...")
    try:
        downloads_path = os.path.expanduser("~/Downloads/")
    except:
        downloads_path = os.path.expanduser("~/İndirilenler")
    file_path = os.path.join(downloads_path, f"PTF_SMF_{selected_start_date[:10]}_{selected_end_date[:10]}.xlsx")
    data.to_excel(file_path)
    st.write("Download complete!")






