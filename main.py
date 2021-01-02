import weight_portfolio
import pandas as pd
from datetime import date, datetime, timedelta

# TODO: vaha pre jeden symbol

# List of symbols you want to use
symbols = ['SPY', 'GLD']

# Time period in days for ATR indicator
atr_time_period = 20

# Time period in years to backtest
test_period_y = 1

# Sum of account in USD
account = 8000

# Display all columns in pandas dataframe
pd.set_option('display.max_columns', None)


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


def backtest_atr_weight(fsymbols, ftest_period_y, fatr_time_period, faccount):
    # Empty variables
    close_atr_data = pd.DataFrame()

    # Set up start and end testing period
    current_year = date.today().year
    test_begin = current_year - ftest_period_y
    test_end = current_year

    # Download data and count ATR for each symbol for each day in the test period
    for symbol in fsymbols:
        downloaded_data = weight_portfolio.data_download_for_backtest(symbol, test_begin, test_end)
        atr_data = weight_portfolio.count_atr(downloaded_data, fatr_time_period)
        close_atr_data['Close_' + symbol] = downloaded_data['Close']
        close_atr_data['ATR_' + symbol] = atr_data['ATR']

    # New column ATR sum
    close_atr_data['ATR_sum'] = close_atr_data.filter(regex='ATR').sum(axis=1)

    # Count weight and shares for each symbol for each day
    close_atr_weight_shares_data = weight_portfolio.count_weight_shares_for_backtest(symbols, close_atr_data, faccount)

    # TODO: prerobit na modifikovatelne
    # close_atr_weight_shares_data obsahuje data za kazy den, ja potrebujem len niektore dni
    # Time period for rebalancing, currently once a month
    # Pick up one day in each month, create new dataframe with just Date-index
    selected_date_data = pd.DataFrame({'Date': []})
    for y in range(test_begin, test_end):
        for m in range(1, 13):
            # Last day in month must be 28th because of February
            select_date = datetime(y, m, 28)

            # If selected date is weekend, decrease the date, check it 4x
            for i in [1, 2, 3, 4]:
                try:
                    close_atr_weight_shares_data.loc[select_date]
                except KeyError:
                    select_date = select_date - timedelta(days=1)
            selected_date_data.loc[len(selected_date_data.index)] = [select_date]

    # Set index
    selected_date_data = selected_date_data.set_index('Date')

    # Temporarly change name of dataframe due long name
    # df = close_atr_weight_shares_selected_data

    # Combine both dataframes, with all data and with just picked up days
    close_atr_weight_shares_selected_data = pd.merge(selected_date_data, close_atr_weight_shares_data, how='left', on='Date')

    # Added columns for previous shares number and difference in shares
    for symbol in symbols:
        close_atr_weight_shares_selected_data['Prev shares' + symbol] = close_atr_weight_shares_selected_data['Shares_' + symbol].shift(1)
        close_atr_weight_shares_selected_data['Diff shares' + symbol] = close_atr_weight_shares_selected_data['Shares_' + symbol] - close_atr_weight_shares_selected_data['Prev shares' + symbol]

    # Create empty column for average price and profit for each symbol
    for symbol in symbols:
        close_atr_weight_shares_selected_data['Avg price_' + symbol] = None
        close_atr_weight_shares_selected_data['Profit_' + symbol] = None

    # Set first average price is close price for each symbol
    for symbol in symbols:
        close_atr_weight_shares_selected_data.iloc[0, close_atr_weight_shares_selected_data.columns.get_loc('Avg price_' + symbol)] = close_atr_weight_shares_selected_data.iloc[0, close_atr_weight_shares_selected_data.columns.get_loc('Close_' + symbol)]

    # How many rebalancing are in the testing period
    number_of_days = range(0, len(close_atr_weight_shares_selected_data.index))

    return close_atr_weight_shares_selected_data


if __name__ == '__main__':

    print(backtest_atr_weight(symbols, test_period_y, atr_time_period, account))

    # output = current_atr_weight(symbols, atr_time_period, account)
    #
    # # Print output df
    # print()
    # print('Data are collected until', output[1])  # TODO: upravit datum, bez casu
    # print()
    # print(output[0])
    #
    # # Print text output
    # print()
    # print('With account ', account, 'you can buy:')
    # for symbol in symbols:
    #     print(int(output[0].loc[symbol, 'Shares']), 'shares of', symbol)
