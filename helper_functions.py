import requests
import json
from snapi_py_client.snapi_bridge import StocknoteAPIPythonBridge
from cryptography.fernet import Fernet

samco = StocknoteAPIPythonBridge()

key = b'W5Zt78GJ62nAlKuIqPSY60iQVx9AOzRpgddsY4JrBps='
user_id = b'gAAAAABg6YDOuuU9oxtEC-YkBtwlsH64FWYtgpSPvX6oo7D8w8SivQgeoSQqIET4J26N5EMlearnm0fDneatRhghNhnuniBPOw=='
password = b'gAAAAABg6YEuPHSYXwA1CHZLu7NkslSsFQC8L5jvCFroG_WtV1qW2UDFOtJV5_owmKwoKo8mEYI99IeVfTHc3SDZ3mioM8mbOQ=='
yob = b'gAAAAABg6YFUdVUeKIp1iy4O0C6GnX5CO0wwA5n8g0kNWDDaLFqW3Rh4MLAgaEjvyXvkWIk1hi5gRjpqiKB5s1t1fsgQjbwvXA=='

cipher_suite = Fernet(key)

def get_session_token():
    
    credentials = {
        'userId': cipher_suite.decrypt(user_id).decode("utf-8") ,
        'password': cipher_suite.decrypt(password).decode("utf-8"),
        'yob': cipher_suite.decrypt(yob).decode("utf-8")
    }
    
    login_headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }

    r = requests.post(
        "https://api.stocknote.com/login",
        data=json.dumps(credentials),
        headers=login_headers
    )

    return dict(r.json())['sessionToken']


def get_daily_data(symbol, from_date, to_date):
    api_headers = {
        'Accept': 'application/json',
        'x-session-token': get_session_token()
    }
    
    results = requests.get(
        "https://api.stocknote.com/history/candleData",
        params={
            "symbolName": symbol,
            "fromDate": from_date,
            "toDate": to_date
        },
        headers=api_headers
    )

    return dict(results.json())['historicalCandleData']


def get_absolute_change(daily_data):
    from_open_value = daily_data[0]['open']
    from_close_value = daily_data[0]['close']
    to_open_value = daily_data[-1]['open']
    to_close_value = daily_data[-1]['close']

    absolute_change = round(((float(to_close_value) - float(from_close_value)) / float(from_close_value)), 2)
    
    return absolute_change


def get_daily_return_trend(daily_data):
    
    total_trading_days = daily_data.__len__()
    positive_trading_days = 0
    negative_trading_days = 0
    neutral_trading_days = 0

    for data in daily_data: 
        open_amount = data['open']
        close_amount = data['close']        

        if open_amount < close_amount:
            positive_trading_days += 1

        elif open_amount > close_amount:
            negative_trading_days += 1

        else: 
            neutral_trading_days += 1

    return round(positive_trading_days/total_trading_days, 2), round(negative_trading_days/total_trading_days, 2)

def get_fip_score(absolute_change, absolute_positive_days, absolute_negative_days):
    if absolute_change > 0:
        fip_score = +1 * (absolute_negative_days - absolute_positive_days)
    
    elif absolute_change < 0: 
        fip_score = -1 * (absolute_negative_days - absolute_positive_days)

    else:
        fip_score = 0.0
        
    return round(fip_score, 2)


def deliver(symbol, from_date, to_date):

    # 1. get the daily data 
    daily_data = get_daily_data(symbol, from_date, to_date)    

    # 2. get the absolute change value
    absolute_change = get_absolute_change(daily_data)

    # 3. get the absolute negative and positive trading days
    absolute_positive_days, absolute_negative_days = get_daily_return_trend(daily_data)

    print(f"Processing done for {symbol}")

    # 4. return the fip score
    return [absolute_change, get_fip_score(absolute_change, absolute_positive_days, absolute_negative_days)]

