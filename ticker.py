import pandas as pd
from twsepy.core import daily_closing_prices, margin_trading, daily_stock_ratios, FIP_trading_data
from twsepy.calendar_manager import CalendarManager
from twsepy.utils import simple_progress_bar

calendar_manager = CalendarManager()

class Ticker:
    def __init__(self, ticker):
        self.ticker = ticker
        self.data = pd.DataFrame(columns=[
            'Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'Transaction Value',
            'Margin Buy', 'Margin Sell', 'Margin Cash Repay', 'Margin Previous Balance', 'Margin Current Balance', 'Margin Next Limit',
            'Short Buy', 'Short Sell', 'Short Repay', 'Short Previous Balance', 'Short Current Balance', 'Short Next Limit', 'Offset',
            'Dividend Yield', 'PE Ratio', 'PB Ratio',
            'FII Buy', 'FII Sell', 'FII Net Buy/Sell', 'Proprietary Buy', 'Proprietary Sell', 'Proprietary Net Buy/Sell',
            'IT Buy', 'IT Sell', 'IT Net Buy/Sell', 'PT Net Buy/Sell', 'PT Buy (Self-trading)', 'PT Sell (Self-trading)',
            'PT Net Buy/Sell (Self-trading)', 'PT Buy (Hedging)', 'PT Sell (Hedging)', 'PT Net Buy/Sell (Hedging)', 'Three Institutional Investors Net Buy/Sell'
        ])

    def download(self, start_date, end_date, select_type='ALLBUT0999'):
        trading_days = calendar_manager.get_trading_dates(start_date, end_date)
        total_days = len(trading_days)

        for i, date in enumerate(trading_days, 1):
            date_str = date.strftime('%Y%m%d')
            date = pd.to_datetime(date_str)

            if date not in self.data['Date'].values:
                self.data = self.data._append({'Date': date}, ignore_index=True)

            self._fetch_daily_closing_prices(date_str)
            self._fetch_margin_trading(date_str)
            self._fetch_daily_stock_ratios(date_str)
            self._fetch_FIP_trading_data(date_str, select_type)

            simple_progress_bar(i, total_days, self.ticker)

    def _fetch_daily_closing_prices(self, date_str):
        df = daily_closing_prices(date_str, 'ALL', 8)
        if df is not None and not df.empty:
            stock_data = df[df.iloc[:, 0] == self.ticker]
            if not stock_data.empty:
                stock_data = stock_data.iloc[0]
                date = pd.to_datetime(date_str)
                self.data.loc[self.data['Date'] == date, ['Open', 'High', 'Low', 'Close', 'Volume', 'Transaction Value']] = [
                    stock_data.iloc[5],  # Opening price
                    stock_data.iloc[6],  # Highest price
                    stock_data.iloc[7],  # Lowest price
                    stock_data.iloc[8],  # Closing price
                    stock_data.iloc[2],  # Trading volume
                    stock_data.iloc[4]   # Transaction value
                ]

    def _fetch_margin_trading(self, date_str):
        df = margin_trading(date_str)
        if df is not None and not df.empty:
            margin_data = df[df.iloc[:, 0] == self.ticker]
            if not margin_data.empty:
                margin_data = margin_data.iloc[0]
                date = pd.to_datetime(date_str)
                self.data.loc[self.data['Date'] == date, [
                    'Margin Buy', 'Margin Sell', 'Margin Cash Repay', 'Margin Previous Balance', 'Margin Current Balance', 'Margin Next Limit', 
                    'Short Buy', 'Short Sell', 'Short Repay', 'Short Previous Balance', 'Short Current Balance', 'Short Next Limit', 'Offset']] = [
                    margin_data.iloc[2],  # Margin buy
                    margin_data.iloc[3],  # Margin sell
                    margin_data.iloc[4],  # Cash repayment
                    margin_data.iloc[5],  # Previous balance
                    margin_data.iloc[6],  # Current balance
                    margin_data.iloc[7],  # Next limit
                    margin_data.iloc[8],  # Short buy
                    margin_data.iloc[9],  # Short sell
                    margin_data.iloc[10], # Short repay
                    margin_data.iloc[11], # Previous balance (short)
                    margin_data.iloc[12], # Current balance (short)
                    margin_data.iloc[13], # Next limit (short)
                    margin_data.iloc[14]  # Offset
                ]

    def _fetch_daily_stock_ratios(self, date_str):
        df = daily_stock_ratios(date_str, 'ALL')
        if df is not None and not df.empty:
            ratio_data = df[df.iloc[:, 0] == self.ticker]
            if not ratio_data.empty:
                ratio_data = ratio_data.iloc[0]
                date = pd.to_datetime(date_str)
                self.data.loc[self.data['Date'] == date, ['Dividend Yield', 'PE Ratio', 'PB Ratio']] = [
                    ratio_data.iloc[2],  # Dividend yield (%)
                    ratio_data.iloc[4],  # PE ratio
                    ratio_data.iloc[5]   # PB ratio
                ]

    def _fetch_FIP_trading_data(self, date_str, select_type='ALL'):
        df = FIP_trading_data(date_str, select_type)
        if df is not None and not df.empty:
            fip_data = df[df.iloc[:, 0] == self.ticker]
            if not fip_data.empty:
                fip_data = fip_data.iloc[0]
                date = pd.to_datetime(date_str)
                self.data.loc[self.data['Date'] == date, [
                    'FII Buy', 'FII Sell', 'FII Net Buy/Sell', 'Proprietary Buy', 'Proprietary Sell', 'Proprietary Net Buy/Sell',
                    'IT Buy', 'IT Sell', 'IT Net Buy/Sell', 'PT Net Buy/Sell', 'PT Buy (Self-trading)', 'PT Sell (Self-trading)',
                    'PT Net Buy/Sell (Self-trading)', 'PT Buy (Hedging)', 'PT Sell (Hedging)', 'PT Net Buy/Sell (Hedging)', 'Three Institutional Investors Net Buy/Sell'
                ]] = [
                    fip_data.iloc[2],  # FII Buy (excluding proprietary trading by foreign investors)
                    fip_data.iloc[3],  # FII Sell (excluding proprietary trading by foreign investors)
                    fip_data.iloc[4],  # FII Net Buy/Sell (excluding proprietary trading by foreign investors)
                    fip_data.iloc[5],  # Proprietary Buy (by foreign investors)
                    fip_data.iloc[6],  # Proprietary Sell (by foreign investors)
                    fip_data.iloc[7],  # Proprietary Net Buy/Sell (by foreign investors)
                    fip_data.iloc[8],  # IT Buy
                    fip_data.iloc[9],  # IT Sell
                    fip_data.iloc[10], # IT Net Buy/Sell
                    fip_data.iloc[11], # PT Net Buy/Sell
                    fip_data.iloc[12], # PT Buy (self-trading)
                    fip_data.iloc[13], # PT Sell (self-trading)
                    fip_data.iloc[14], # PT Net Buy/Sell (self-trading)
                    fip_data.iloc[15], # PT Buy (hedging)
                    fip_data.iloc[16], # PT Sell (hedging)
                    fip_data.iloc[17], # PT Net Buy/Sell (hedging)
                    fip_data.iloc[18]  # Three Institutional Investors Net Buy/Sell
                ]

# Usage example:
# ticker = Ticker('2330')  # Example ticker symbol for TSMC
# ticker.download('20230601', '20230630')
# print(ticker.data)
