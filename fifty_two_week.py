# This file can be run by itself to update the df/csv of stocks near their 52-week high (within 2%)
# The class Refresh52Week is called from the portfolio3.0.py file to do the same

from ib_insync import *
import pandas as pd
import os


# Function to fetch historical data and check if at 52-week high
class Refresh52Week:
    def check_52_week_high(ticker, ib):
        contract = Stock(ticker, 'SMART', 'USD')
        bars = ib.reqHistoricalData(
            contract,
            endDateTime='',
            durationStr='1 Y',
            barSizeSetting='1 day',
            whatToShow='TRADES',
            useRTH=True,
            formatDate=1)
        df = util.df(bars)
        df['52_week_high'] = df['high'].max()
        #df['52_week_high'] = df['high'].rolling(window=252).max()
        current_price = df.iloc[-1]['close']  # Assuming last row is current price
        high_price = df.iloc[-1]['52_week_high']
        is_at_high = (current_price >= high_price*0.98)
        return is_at_high

    # Function to process CSV file
    def process_csv(file_path, ib):
        # Read CSV file into DataFrame
        df = pd.read_csv(file_path)
        # Iterate through tickers in the 'A' column
        for index, row in df.iterrows():
            ticker = row['Stock Symbol']
            try:
                is_at_high = Refresh52Week.check_52_week_high(ticker, ib)
                df.loc[index, '52_week_high'] = is_at_high
            except Exception as e:
                print(f"Error fetching data for {ticker}: {e}")
                df.loc[index, '52_week_high'] = False  # Assuming not at high on error
        df['Stop Loss Today'] = False
        # Save updated DataFrame back to CSV
        df.to_csv(file_path, index=False)
        high_tickers = df[df['52_week_high'] == True]
        high_tickers.to_csv(r'C:\Users\johnm\OneDrive\Desktop\Fintech\52weekTrue.csv', index=False)
        print(f"Updated CSV file saved: {file_path}")

    def main(ib):
        #ib = IB()
        csv_file = r'C:\Users\johnm\OneDrive\Desktop\Fintech\fortune100_stock_symbols.csv'
        if os.path.exists(csv_file):
            Refresh52Week.process_csv(csv_file, ib)
        else:
            print(f"File not found: {csv_file}")


'''
ib = IB()
ib.connect('127.0.0.1', 7497, clientId=2)
ib.reqMarketDataType(1)  # 1 is live prices
Refresh52Week.main(ib)  # allows to run file by itself
ib.disconnect()
'''