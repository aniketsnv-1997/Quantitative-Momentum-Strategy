# get the library imports for the code
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from helper_functions import deliver, get_daily_data, get_last_traded_price
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

sidebar_form = st.sidebar.form(key='get_absolute_momentum')
momentum_from_date = sidebar_form.date_input('Strategy Start Date')
momentum_to_date = sidebar_form.date_input('Strategy End Date')

# check box to save the df or not
check = sidebar_form.checkbox('Save the new processed data as a ".csv" file')

submit = sidebar_form.form_submit_button(label='Submit')

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

st.text(" ")

col1, col2 = st.beta_columns(2)

col1.markdown("## Paper Trading - Quantitative Momentum")

form = col2.form(key='refresh_form')
refresh = form.form_submit_button("Refresh")

top_25 = pd.read_csv("final_list.csv")

paper_trade_data = pd.DataFrame()

open_amount_list = [
    685.95,
    1440.05,
    683.6,
    195.8,
    1010.5,
    1552.55,
    1251.7,
    4595,
    855.05,
    412,
    126.95,
    92.7,
    2819.65,
    780,
    143.8,
    310.85,
    275.05,
    1953.95,
    4325.05,
    719.5,
    642.4,
    1097.9,
    927,
    350.35,
    369
]

paper_trade_data['STOCK'] = top_25['Symbol']
paper_trade_data['PURCHASE_DATE'] = "12-07-2021"
paper_trade_data['INVESTED_AMOUNT'] = 4000
paper_trade_data['STOCK_PRICE_AT_INVESTMENT_DATE'] = open_amount_list
paper_trade_data['UNITS_BOUGHT'] = round(paper_trade_data['INVESTED_AMOUNT'] / paper_trade_data['STOCK_PRICE_AT_INVESTMENT_DATE'], 2)
paper_trade_data['CURRENT_MARKET_PRICE'] = top_25['Symbol'].apply(get_last_traded_price)
paper_trade_data['CURRENT_VALUE'] = round(paper_trade_data['CURRENT_MARKET_PRICE'].astype(float) * paper_trade_data['UNITS_BOUGHT'].astype(float), 2)
paper_trade_data['GAINS (IN %)'] = round(((paper_trade_data['CURRENT_VALUE'] - paper_trade_data['INVESTED_AMOUNT']) / paper_trade_data['INVESTED_AMOUNT']) * 100, 2)

if refresh:
    paper_trade_data['STOCK'] = top_25['Symbol']
    paper_trade_data['PURCHASE_DATE'] = "12-07-2021"
    paper_trade_data['INVESTED_AMOUNT'] = 4000
    paper_trade_data['STOCK_PRICE_AT_INVESTMENT_DATE'] = open_amount_list
    paper_trade_data['UNITS_BOUGHT'] = round((paper_trade_data['INVESTED_AMOUNT'] / paper_trade_data['STOCK_PRICE_AT_INVESTMENT_DATE']).astype(float), 2)
    paper_trade_data['CURRENT_MARKET_PRICE'] = top_25['Symbol'].apply(get_last_traded_price)
    paper_trade_data['CURRENT_VALUE'] = round(paper_trade_data['CURRENT_MARKET_PRICE'].astype(float) * paper_trade_data['UNITS_BOUGHT'].astype(float), 2)
    paper_trade_data['GAINS (IN %)'] = round(((paper_trade_data['CURRENT_VALUE'] - paper_trade_data['INVESTED_AMOUNT']) / paper_trade_data['INVESTED_AMOUNT']) * 100, 2)
    
st.dataframe(paper_trade_data, width=None, height=None)

col1, col2, col3 = st.beta_columns(3)

total_gains_in_percent = ((paper_trade_data['CURRENT_VALUE'].sum() - paper_trade_data['INVESTED_AMOUNT'].sum()) / paper_trade_data['INVESTED_AMOUNT'].sum()) * 100

col1.markdown(f" #### Invested Amount: {paper_trade_data['INVESTED_AMOUNT'].sum()} INR")
col2.markdown(f" #### Current Value: {paper_trade_data['CURRENT_VALUE'].sum()} INR")
col3.markdown(f" #### Total Gains (In %): {round(total_gains_in_percent, 2)}")

st.text(" ")


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
daily_data = get_daily_data(company, from_date, to_date, False)
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

col2.subheader("Sector Specific")
industry = col2.selectbox('Industry', nifty.Industry.to_list())
col2.dataframe(data=nifty[nifty['Industry'] == industry], width=None, height=None)