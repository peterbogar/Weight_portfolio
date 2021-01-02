import weight_portfolio
import pandas as pd

# List of symbols you want to use
symbols = ['SPY', 'GLD']

# Time period in days for ATR indicator
atr_time_period = 20

# Sum of account in USD
account = 8000


def current_atr_weight(fsymbols, fatr_time_period, faccount):
    # Function will take current market data from Yahoo
    # Count ATR (Average True Range)- volatility
    # Weigh each symbol by ATR in reverse order (higher ATR=lower weight)

    # Empty variables
    last_day = 0
    symbol_close_atr_data = pd.DataFrame({'Symbol': [], 'Close': [], 'ATR': [], 'Weight': [], 'Shares': []})

    # Download price and count ATR for each symbol
    for fsymbol in fsymbols:
        downloaded_data = weight_portfolio.data_download(symbol=fsymbol, time_period_days=atr_time_period)
        atr_data = weight_portfolio.count_atr(downloaded_data, atr_time_period=fatr_time_period)

        # Last day, last close, last ATR
        last_day = downloaded_data.index[-1]
        close_price = downloaded_data.iloc[-1][3]
        last_atr = atr_data.iloc[-1][-1]

        # Collect all data to new df
        symbol_close_atr_data.loc[len(symbol_close_atr_data.index)] = [fsymbol, close_price, last_atr, 0, 0]

    # Set Symbol as a index in output df
    symbol_close_atr_data = symbol_close_atr_data.set_index('Symbol')

    symbol_close_atr_weight_shares_data = weight_portfolio.count_weight_shares(close_atr_data_all=symbol_close_atr_data, account=faccount)

    return symbol_close_atr_weight_shares_data, last_day


if __name__ == '__main__':

    output = current_atr_weight(symbols, atr_time_period, account)

    # Print output df
    print()
    print('Data are collected until', output[1])  # TODO: upravit datum, bez casu
    print()
    print(output[0])

    # Print text output
    print()
    print('With account ', account, 'you can buy:')
    for symbol in symbols:
        print(int(output[0].loc[symbol, 'Shares']), 'shares of', symbol)
