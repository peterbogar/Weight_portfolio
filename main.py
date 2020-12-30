# Script will take current market data from Yahoo
# Count ATR (Average True Range)- volatility
# Weigh each symbol by ATR in reverse order (higher ATR=lower weight)
# Divide account among symbols- how many shares you can buy

import weight_portfolio
import pandas as pd
from datetime import date, timedelta

# List of symbols you want to use
symbols = ['SLV', 'TLT', 'XLE', 'XLF']

# Time period for ATR indicator
time_period = 20

# Sum of account in USD
account = 8000


if __name__ == '__main__':
    # Empty dataframe
    collected_data = pd.DataFrame({'Symbol': [], 'Close': [], 'ATR': [], 'Weight': [], 'Shares': []})

    # Load of price and count ATR for each symbol
    for symbol in symbols:
        downloaded_data = weight_portfolio.data_download(symbol=symbol, time_period=time_period)
        atr = weight_portfolio.count_atr(downloaded_data, atr_time_period=time_period)

        last_day = downloaded_data.index[-1]
        close_price = downloaded_data.iloc[-1][3]

        collected_data.loc[len(collected_data.index)] = [symbol, close_price, atr, 0, 0]

    # Set Symbol as a index in output table
    collected_data = collected_data.set_index('Symbol')

    # Print output table
    print()
    print('Data are collected until', date.today() - timedelta(days=1))
    print()
    output_table = weight_portfolio.count_weight(collected_data=collected_data, account=account)
    print(output_table)

    # Print text output
    print()
    print('With account ', account, 'you can buy:')
    for symbol in symbols:
        print(int(output_table.loc[symbol, 'Shares']), 'shares of', symbol)
