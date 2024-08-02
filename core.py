import pandas as pd
from .config import DEFAULT_HEADERS, BASE_URL
from .exceptions import RequestFailedException, JSONDecodeException
from twsepy.utils import RateLimiter
from .utils import limited_request, remove_html_tags
import json

# Global default rate limiter 
# No idea how to remove it.
default_rate_limiter = RateLimiter(rate_limit=5, period=5, enabled = False)

def daily_closing_prices(date, select_type='ALL', table_index=8, proxy=None, rate_limiter=default_rate_limiter):
    """
    Fetch daily closing prices from the TWSE.

    :param date: The date for which to fetch the data (format: YYYYMMDD).
    :param select_type: The type of data to select.
    :param table_index: The index of the table to extract from the response.
        :reference: https://www.twse.com.tw/zh/trading/historical/mi-index.html
            :category: "ALL". Index start from 0.
            :more information in README.md
    :param proxy: Optional proxy settings for the request.
    :return type:  DataFrame.
    """
    url = f"{BASE_URL}/afterTrading/MI_INDEX"
    params = {
        'date': date,
        'type': select_type,
        'response': 'json'
    }

    response = limited_request(url, headers=DEFAULT_HEADERS, params=params, proxy=proxy, rate_limiter=default_rate_limiter)
    if response.status_code == 200:
        try:
            data = response.json()
        except json.JSONDecodeError:
            raise JSONDecodeException("Failed to parse JSON response.", response.text)

        if table_index < len(data.get('tables', [])):
            table = data['tables'][table_index]
            df = pd.DataFrame(table['data'], columns=table['fields'])
            if len(df.columns) > 9:
                df.iloc[:, 9] = df.iloc[:, 9].apply(remove_html_tags)
            return df
        else:
            print(f"Table index {table_index} is out of range.")
            return pd.DataFrame()
    else:
        raise RequestFailedException(
            f"Failed to retrieve data for {date} with type {select_type}. Status code: {response.status_code}")


def market_trading_info(date, proxy=None, rate_limiter=default_rate_limiter):
    """
    Fetch market trading information from the TWSE.
    :reference: https://www.twse.com.tw/zh/trading/historical/fmtqik.html

    :param date: The date for which to fetch the data (format: YYYYMMDD).
    :param proxy: Optional proxy settings for the request.
    :return type:  DataFrame.
    """
    url = f"{BASE_URL}/afterTrading/FMTQIK"
    params = {
        'date': date,
        'response': 'json'
    }

    response = limited_request(url, headers=DEFAULT_HEADERS, params=params, proxy=proxy, rate_limiter=default_rate_limiter)
    if response.status_code == 200:
        try:
            data = response.json()
        except json.JSONDecodeError:
            raise JSONDecodeException("Failed to parse JSON response.", response.text)

        if 'data' in data:
            df = pd.DataFrame(data['data'], columns=data['fields'])
            return df
        else:
            print(f"No data found for {date}.")
            return pd.DataFrame()
    else:
        raise RequestFailedException(
            f"Failed to retrieve data for {date}. Status code: {response.status_code}")


def daily_stock_ratios(date, select_type, proxy=None, rate_limiter=default_rate_limiter):
    """
    Fetch daily stock ratios (e.g., PE ratio, dividend yield) from the TWSE.
    :reference: https://www.twse.com.tw/zh/trading/historical/bwibbu-day.html
    :param date: The date for which to fetch the data (format: YYYYMMDD).
    :param select_type: The type of data to select.
    :param proxy: Optional proxy settings for the request.
    :return type:  DataFrame.
    """
    url = f"{BASE_URL}/afterTrading/BWIBBU_d"
    params = {
        'date': date,
        'selectType': select_type,
        'response': 'json'
    }

    response = limited_request(url, headers=DEFAULT_HEADERS, params=params, proxy=proxy, rate_limiter=rate_limiter)
    if response.status_code == 200:
        try:
            data = response.json()
        except json.JSONDecodeError:
            raise JSONDecodeException("Failed to parse JSON response.", response.text)

        if 'data' in data:
            df = pd.DataFrame(data['data'], columns=data['fields'])
            return df
        else:
            print(f"No data for {date} with type {select_type}.")
            return pd.DataFrame()
    else:
        raise RequestFailedException(
            f"Failed to retrieve data for {date} with type {select_type}. Status code: {response.status_code}")


def margin_trading(date, proxy=None, rate_limiter=default_rate_limiter):
    """
    Fetch margin trading information from the TWSE.
    :reference: https://www.twse.com.tw/zh/trading/margin/mi-margn.html
    :param date: The date for which to fetch the data (format: YYYYMMDD).
    :param proxy: Optional proxy settings for the request.
    :return type:  DataFrame.
    """
    url = f"{BASE_URL}/marginTrading/MI_MARGN"
    params = {
        'date': date,
        'selectType': 'STOCK',
        'response': 'json'
    }

    response = limited_request(url, headers=DEFAULT_HEADERS, params=params, proxy=proxy, rate_limiter=rate_limiter)
    if response.status_code == 200:
        try:
            data = response.json()
        except json.JSONDecodeError:
            raise JSONDecodeException("Failed to parse JSON response.", response.text)

        if 'tables' in data and len(data['tables']) > 1:
            table = data['tables'][1]
            fields = table['fields']
            rows = table['data']
            df = pd.DataFrame(rows, columns=fields)
            df['Date'] = date
            df.set_index('Date', inplace=True)
            return df
        else:
            print(f"No data for {date}. Skipping.")
            return pd.DataFrame()
    else:
        raise RequestFailedException(
            f"Failed to retrieve data for {date} with type 'margin_trading'. Status code: {response.status_code}")


def FIP_trading_data(date, select_type='ALL', proxy=None, rate_limiter=default_rate_limiter):
    """
    F: Foreign Institutional Investors (FII)
    I: Investment Trusts (IT)
    P: Proprietary Traders (PT)

    Fetch institutional trading data from the TWSE.
    :reference: https://www.twse.com.tw/zh/trading/foreign/t86.html
    :param date: The date for which to fetch the data (format: YYYYMMDD).
    :param select_type: The type of data to select.
        :more information in README.md
    :param proxy: Optional proxy settings for the request.
    :return type: DataFrame.
    """
    url = f"{BASE_URL}/fund/T86"
    params = {
        'date': date,
        'selectType': select_type,
        'response': 'json'
    }

    response = limited_request(url, headers=DEFAULT_HEADERS, params=params, proxy=proxy, rate_limiter=rate_limiter)
    if response.status_code == 200:
        try:
            data = response.json()
        except json.JSONDecodeError:
            raise JSONDecodeException("Failed to parse JSON response.", response.text)

        if 'data' in data:
            df = pd.DataFrame(data['data'], columns=data['fields'])
            return df
        else:
            print(f"No data for {date} with type {select_type}.")
            return pd.DataFrame()
    else:
        raise RequestFailedException(
            f"Failed to retrieve data for {date} with type {select_type}. Status code: {response.status_code}")
