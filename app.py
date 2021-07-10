# get the library imports for the code
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from helper_functions import deliver, get_daily_data
import time
import numpy as np
from datetime import datetime as dt
from datetime import timedelta

st.set_page_config(page_title="Quantitative Momentum Strategy", page_icon=None, layout='wide', initial_sidebar_state='auto')

# initialize today's date for further use
today = dt.today().date()
# start_date = today - timedelta(days=31)
# end_date = today - timedelta(days=361)

# Main Webpage Elements

st.title("Quantitative Momentum Strategy")

st.markdown("""
This app ranks the **CNX 500** listed stocks in the highest order of the following two metrics!
* **Generic Momentum:** [Wikipedia](https://en.wikipedia.org/wiki/Momentum_investing)
* **Frog In the Pan Score (FIP Score):** [Wikipedia](http://www.stagirit.org/sites/default/files/articles/a_0280_frog_in_the_pan_identifying_the_highest_quality_momentum_stocks_-_alpha_architect.pdf).
""")

# read the data from the source csv file
nifty = pd.read_csv("ind_nifty500list.csv")
static_list = pd.read_csv("final_list.csv")

'''
    ## Top 25 High Performing Stocks
'''

# SideBar Elements
st.sidebar.title("Configuration Panel")

st.sidebar.write('Press submit to get the momentum ranking on your desired time scale')

form = st.sidebar.form(key='my_form')
momentum_from_date = form.date_input('Strategy Start Date')
momentum_to_date = form.date_input('Strategy End Date')

# check box to save the df or not
check = st.sidebar.checkbox('Save the new processed data as a ".csv" file')

submit = form.form_submit_button(label='Submit')

# if the user submits the start and end date for the strategy, then only execute the logic to get the historical data
if submit:

    with st.spinner("Wait for the new data to be generated"):
        time.sleep(50)

    # create a temporary dataframe to store the function returned values
    temp = pd.DataFrame()

    temp['Output'] = nifty['Symbol'].apply(deliver, from_date=momentum_from_date, to_date=momentum_to_date)

    nifty[['Absolute_Momentum', 'FIP_Score']] = pd.DataFrame(temp.Output.tolist())

    nifty_fifty = nifty.sort_values(by=['Absolute_Momentum'], ascending=[False]).reset_index(drop=True).head(50)
    nifty_twenty_five = nifty_fifty.sort_values(by=['FIP_Score'], ascending=[True]).reset_index(drop=True).head(25)
        
    if check:
        nifty_twenty_five.to_csv("final_list.csv", index=False)

    st.success("Yayyy!! It's Done!")

    st.text(f"from {momentum_from_date} to {momentum_to_date}")
    st.dataframe(data=nifty_twenty_five, width=None, height=None)

else:
    st.text(f"from July 10, 2020 to June 10, 2021")
    st.dataframe(data=static_list, width=None, height=None)

'''
    ## Stock Historical Behavior 
'''

options_expander = st.beta_expander("Additional Filters")

# define the two column objects to be made
col1, col2, col3 = options_expander.beta_columns(3)

company = col1.selectbox('Company', nifty.Symbol.to_list())
temp = today - timedelta(days=60)
from_date = col2.date_input("From", value=temp)
to_date = col3.date_input("To", value=today)

col1, col2 = st.beta_columns(2)

# get the samco api data for the selected company for the selected time period
daily_data = get_daily_data(company, from_date, to_date)
daily_data_df = pd.DataFrame(daily_data)
col1.dataframe(data=daily_data_df, width=None, height=370)

fig = go.Figure(
    data=[go.Candlestick(x=daily_data_df['date'],
    open=daily_data_df['open'],
    high=daily_data_df['high'],
    low=daily_data_df['low'],
    close=daily_data_df['close'])]
)

fig.update_layout(
    title='The Steady Rise - ' + company,
    yaxis_title="Stock Price (In INR)",
    xaxis_title="Date"
)

col2.plotly_chart(fig)

'''
    ## Base Table View
'''
col1, col2 = st.beta_columns(2)
col1.subheader("Company Specific")
companies = col1.multiselect('Select the company for which you want to view the data:', nifty.Symbol.to_list())

# display the base NSE data
if companies.__len__() == 0:
    col1.dataframe(data=nifty, width=None, height=None)
else:
    col1.dataframe(data=nifty[np.isin(nifty['Symbol'], companies)], width=None, height=None)

col2.subheader("Sectore Specific")
industry = col2.selectbox('Industry', nifty.Industry.to_list())
col2.dataframe(data=nifty[nifty['Industry'] == industry], width=None, height=None)

# '''
#     ## Had You Invested in this Strategy with...
# '''

# col1, col2, col3 = st.beta_columns(3)
# amount = col1.number_input("Rupees (In INR)", min_value = 0)
# temp = today - timedelta(days=28)
# start = col2.date_input("From Date", value=temp)
# end = col3.date_input("To Date", value=today)