import pandas as pd
from twsepy.core import daily_closing_prices, margin_trading, daily_stock_ratios, FIP_trading_data
from twsepy.calendar_manager import CalendarManager
from twsepy.utils import RateLimiter
from twsepy.utils import simple_progress_bar

calendar_manager = CalendarManager()
# Global default rate limiter
# No idea how to remove it.
default_rate_limiter = RateLimiter(rate_limit=5, period=5, enabled = False)

class Ticker:
    def __init__(self, ticker, rate_limiter=default_rate_limiter):
        self.ticker = ticker
        self.rate_limiter = rate_limiter
        self.data_columns = [
            'Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'Transaction Value',
            'Margin Buy', 'Margin Sell', 'Margin Cash Repay', 'Margin Previous Balance', 'Margin Current Balance', 'Margin Next Limit',
            'Short Buy', 'Short Sell', 'Short Repay', 'Short Previous Balance', 'Short Current Balance', 'Short Next Limit', 'Offset',
            'Dividend Yield', 'PE Ratio', 'PB Ratio',
            'FII Buy', 'FII Sell', 'FII Net Buy/Sell', 'Proprietary Buy', 'Proprietary Sell', 'Proprietary Net Buy/Sell',
            'IT Buy', 'IT Sell', 'IT Net Buy/Sell', 'PT Net Buy/Sell', 'PT Buy (Self-trading)', 'PT Sell (Self-trading)',
            'PT Net Buy/Sell (Self-trading)', 'PT Buy (Hedging)', 'PT Sell (Hedging)', 'PT Net Buy/Sell (Hedging)', 'Three Institutional Investors Net Buy/Sell'
        ]
        self.data = pd.DataFrame(columns=self.data_columns)

    def download(self, start_date, end_date, select_type='ALLBUT0999'):
        trading_days = calendar_manager.get_trading_dates(start_date, end_date)
        total_days = len(trading_days)
        data_list = []

        for i, date in enumerate(trading_days, 1):
            date_str = date.strftime('%Y%m%d')
            date = pd.to_datetime(date_str)
            row_data = {'Date': date}

            row_data.update(self._fetch_daily_closing_prices(date_str))
            row_data.update(self._fetch_margin_trading(date_str))
            row_data.update(self._fetch_daily_stock_ratios(date_str))
            row_data.update(self._fetch_FIP_trading_data(date_str, select_type))

            data_list.append(row_data)
            simple_progress_bar(i, total_days, self.ticker)

        if data_list:
            new_data = pd.DataFrame(data_list, columns=self.data_columns)
            self.data = pd.concat([self.data, new_data], ignore_index=True)

    def _fetch_daily_closing_prices(self, date_str):
        df = daily_closing_prices(date_str, 'ALL', 8, rate_limiter=self.rate_limiter)
        if df is not None and not df.empty:
            stock_data = df[df.iloc[:, 0] == self.ticker]
            if not stock_data.empty:
                stock_data = stock_data.iloc[0]
                return {
                    'Open': stock_data.iloc[5],
                    'High': stock_data.iloc[6],
                    'Low': stock_data.iloc[7],
                    'Close': stock_data.iloc[8],
                    'Volume': stock_data.iloc[2],
                    'Transaction Value': stock_data.iloc[4]
                }
        return {}

    def _fetch_margin_trading(self, date_str):
        df = margin_trading(date_str, rate_limiter=self.rate_limiter)
        if df is not None and not df.empty:
            margin_data = df[df.iloc[:, 0] == self.ticker]
            if not margin_data.empty:
                margin_data = margin_data.iloc[0]
                return {
                    'Margin Buy': margin_data.iloc[2],
                    'Margin Sell': margin_data.iloc[3],
                    'Margin Cash Repay': margin_data.iloc[4],
                    'Margin Previous Balance': margin_data.iloc[5],
                    'Margin Current Balance': margin_data.iloc[6],
                    'Margin Next Limit': margin_data.iloc[7],
                    'Short Buy': margin_data.iloc[8],
                    'Short Sell': margin_data.iloc[9],
                    'Short Repay': margin_data.iloc[10],
                    'Short Previous Balance': margin_data.iloc[11],
                    'Short Current Balance': margin_data.iloc[12],
                    'Short Next Limit': margin_data.iloc[13],
                    'Offset': margin_data.iloc[14]
                }
        return {}

    def _fetch_daily_stock_ratios(self, date_str):
        df = daily_stock_ratios(date_str, 'ALL', rate_limiter=self.rate_limiter)
        if df is not None and not df.empty:
            ratio_data = df[df.iloc[:, 0] == self.ticker]
            if not ratio_data.empty:
                ratio_data = ratio_data.iloc[0]
                return {
                    'Dividend Yield': ratio_data.iloc[2],
                    'PE Ratio': ratio_data.iloc[4],
                    'PB Ratio': ratio_data.iloc[5]
                }
        return {}

    def _fetch_FIP_trading_data(self, date_str, select_type='ALL'):
        df = FIP_trading_data(date_str, select_type, rate_limiter=self.rate_limiter)
        if df is not None and not df.empty:
            fip_data = df[df.iloc[:, 0] == self.ticker]
            if not fip_data.empty:
                fip_data = fip_data.iloc[0]
                return {
                    'FII Buy': fip_data.iloc[2],
                    'FII Sell': fip_data.iloc[3],
                    'FII Net Buy/Sell': fip_data.iloc[4],
                    'Proprietary Buy': fip_data.iloc[5],
                    'Proprietary Sell': fip_data.iloc[6],
                    'Proprietary Net Buy/Sell': fip_data.iloc[7],
                    'IT Buy': fip_data.iloc[8],
                    'IT Sell': fip_data.iloc[9],
                    'IT Net Buy/Sell': fip_data.iloc[10],
                    'PT Net Buy/Sell': fip_data.iloc[11],
                    'PT Buy (Self-trading)': fip_data.iloc[12],
                    'PT Sell (Self-trading)': fip_data.iloc[13],
                    'PT Net Buy/Sell (Self-trading)': fip_data.iloc[14],
                    'PT Buy (Hedging)': fip_data.iloc[15],
                    'PT Sell (Hedging)': fip_data.iloc[16],
                    'PT Net Buy/Sell (Hedging)': fip_data.iloc[17],
                    'Three Institutional Investors Net Buy/Sell': fip_data.iloc[18]
                }
        return {}

# Usage example:
# ticker = Ticker('2330')  # Example ticker symbol for TSMC
# ticker.download('20230601', '20230630')
# print(ticker.data)
