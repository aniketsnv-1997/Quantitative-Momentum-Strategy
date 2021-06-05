# get the library imports for the code
# pypiwin32==301
import streamlit as st
from pandas_datareader import data
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import requests
from datetime import datetime as dt
from datetime import timedelta
from itertools import islice

st.set_page_config(page_title="Quantitative Momentum Strategy", page_icon=None, layout='wide', initial_sidebar_state='auto')

today = dt.today().date()
# start_date = today - timedelta(days=31)
# end_date = today - timedelta(days=361)

st.title("Quantitative Momentum Strategy")

st.markdown("""
This app ranks the **CNX 500** listed stocks in the highest order of the following two metrics!
* **Generic Momentum:** [Wikipedia](https://en.wikipedia.org/wiki/Momentum_investing)
* **Frog In the Pan Score (FIP Score):** [Wikipedia](http://www.stagirit.org/sites/default/files/articles/a_0280_frog_in_the_pan_identifying_the_highest_quality_momentum_stocks_-_alpha_architect.pdf).
""")

st.sidebar.title("Configuration Panel")

st.sidebar.write('Press submit to get the momentum ranking on your desired time scale')

form = st.sidebar.form(key='my_form')
sd = form.date_input('Start Date')
ed = form.date_input('End Date')

submit = form.form_submit_button(label='Submit')

# read the data from the source csv file
nifty = pd.read_csv("ind_nifty500list.csv")

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

'''
    ## Stock Historical Behavior 
'''

# define the two column objects to be made
col1, col2, col3, col4 = st.beta_columns(4)

company = col1.selectbox('Company', nifty.Symbol.to_list())
temp = today - timedelta(days=28)
start = col2.date_input("Start Date", value=temp)
end = col3.date_input("End Date", value=today)
metrics = col4.multiselect("Metrics", ['Open', 'Close', 'Volume'])

col1, col2 = st.beta_columns(2)
# get the yahoo finance data for the selected company for the selected time period
df = data.DataReader(name=company+".NS", data_source="yahoo", start=str(start), end=str(end))
df = df.reset_index()
col1.dataframe(data=df, width=None, height=None)

if metrics.__len__() == 0:
    col2.line_chart(df)
else:
    col2.line_chart(df[metrics])


# if the user submits the start and end date for the strategy, then only execute the logic to get the historical data
if submit:
    print(sd)
    print(ed)

    length_to_split = [100, 100, 100, 100, 98]

    symbols = nifty['Symbol'].to_list()
    symbols.remove('INDUSTOWER')
    symbols.remove('STLTECH')
    symbols.remove('ATGL')

    # Using islice to split the 498 symbol list into 5 lists of 100 elements each
    i_symbols = iter(symbols)
    o_symbols = [list(islice(i_symbols, elem)) for elem in length_to_split]

    j = 1
    for li in o_symbols:
        for i in li:
            print(j)
            print(i)
            index = nifty[nifty['Symbol'] == i].index

            df = data.DataReader(name=i+".NS", data_source="yahoo", start=str(sd), end=str(ed))
            df = df.reset_index()
            print(df)
            # assign the start date open close values and end date open close values
            nifty.at[index, 'Open_Start'] = df[df['Date'] == pd.to_datetime(sd)]['Open'].iloc[0]
            nifty.at[index, 'Open_End'] = df[df['Date'] == pd.to_datetime(ed)]['Open'].iloc[0]
            nifty.at[index, 'Close_Start'] = df[df['Date'] == pd.to_datetime(sd)]['Close'].iloc[0]
            nifty.at[index, 'Close_End'] = df[df['Date'] == pd.to_datetime(sd)]['Close'].iloc[0]

            # get the indices of the rows in df where the return is positive, negative and neutral
            df['Returns'] = round(df['Close'] - df['Open'], 2)
            positive_index = df[df['Returns'] > 0].index
            negative_index = df[df['Returns'] < 0].index

            # assign the appropriate labels to the relevant indices
            df.at[positive_index, 'Type'] = 'Positive'
            df.at[negative_index, 'Type'] = 'Negative'

            # get the % of the negative, positive and the neutral count
            nifty.at[index, 'Negative'] = round(df.Type.value_counts().iloc[0]/df.shape[0], 2)
            nifty.at[index, 'Positive'] = round(df.Type.value_counts().iloc[1]/df.shape[0], 2)

            j += 1

        print(nifty.shape)

    nifty.to_csv("final_list.csv",index=False)


