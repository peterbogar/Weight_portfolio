import weight_portfolio
import single_stock
import pandas as pd
from datetime import date, datetime, timedelta

# List of symbols you want to use
symbols = ['SPY', 'XLE']

# Time period in days for ATR indicator
atr_time_period = 2

# Time period in years to backtest
test_period_y = 10

# Sum of account in USD
account = 10000
# Reinvestovanie profitu je prilis zlozite na backtest

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
            for _ in [1, 2, 3, 4]:
                try:
                    close_atr_weight_shares_data.loc[select_date]
                except KeyError:
                    select_date = select_date - timedelta(days=1)
            selected_date_data.loc[len(selected_date_data.index)] = [select_date]

    # Set index
    selected_date_data = selected_date_data.set_index('Date')

    # Combine both dataframes, with all data and with just picked up days
    df = pd.merge(selected_date_data, close_atr_weight_shares_data, how='left', on='Date')

    # Added columns for previous shares number and difference in shares
    for symbol in symbols:
        df['Prev shares' + symbol] = df['Shares_' + symbol].shift(1)
        df['Diff shares' + symbol] = df['Shares_' + symbol] - df['Prev shares' + symbol]

    # Create empty column for average price and profit for each symbol
    for symbol in symbols:
        df['Avg price_' + symbol] = None
        df['Profit_' + symbol] = None
        # df['Cum profit_' + symbol] = None

    # Set first average price is close price for each symbol
    for symbol in symbols:
        df.iloc[0, df.columns.get_loc('Avg price_' + symbol)] = df.iloc[0, df.columns.get_loc('Close_' + symbol)]

    # How many rebalancing are in the testing period
    number_of_days = range(0, len(df.index))

    # For each symbol count average price and profit in separate functions
    for symbol in symbols:
        for index in number_of_days:
            if index == 0:
                pass
            else:
                # Set variables for function 'count average price' and 'count profit'
                diff = df.iloc[index, df.columns.get_loc('Diff shares' + symbol)]
                close_price = df.iloc[index, df.columns.get_loc('Close_' + symbol)]
                shares = df.iloc[index, df.columns.get_loc('Shares_' + symbol)]
                previous_shares = df.iloc[index, df.columns.get_loc('Prev shares' + symbol)]
                previous_avg_price = df.iloc[index - 1, df.columns.get_loc('Avg price_' + symbol)]

                # Count average price in function
                df.iloc[index, df.columns.get_loc('Avg price_' + symbol)] = weight_portfolio.count_avg_price_for_backtest(diff, close_price, shares, previous_shares, previous_avg_price)

                # Count profit in function
                avg_price = df.iloc[index, df.columns.get_loc('Avg price_' + symbol)]
                df.iloc[index, df.columns.get_loc('Profit_' + symbol)] = weight_portfolio.count_profit_for_backtest(diff, close_price, avg_price)

    # Count cumulative profit for each symbol
    for symbol in symbols:
        df['Cum_profit_'+symbol] = df['Profit_'+symbol].cumsum()

    # Change dataframe name
    close_atr_weight_shares_selected_cumprofit_data = df

    return close_atr_weight_shares_selected_cumprofit_data


def backtest_summary(fdata):
    # Summarize cumulative profit among all symbols
    cum_profit_data = fdata.filter(regex='Cum').copy()
    cum_profit_data['Sum profit'] = cum_profit_data.sum(axis=1)

    # Numbers of days for backtest (index)
    number_of_days = range(0, len(cum_profit_data.index))

    # Add new column Peak and Drawdown for each symbol, first row is 0
    for symbol in symbols:
        cum_profit_data.loc[cum_profit_data.index[0], 'Peak_'+symbol] = 0
        cum_profit_data.loc[cum_profit_data.index[0], 'DD%_' + symbol] = 0

    # Peak in profit for symbols
    for symbol in symbols:
        # Column- symbol
        column_profit = cum_profit_data.columns.get_loc('Cum_profit_'+symbol)
        column_peak = cum_profit_data.columns.get_loc('Peak_'+symbol)
        column_dd = cum_profit_data.columns.get_loc('DD%_'+symbol)

        # Row- index
        for row in number_of_days:
            curr_profit = cum_profit_data.iloc[row, column_profit]
            curr_peak = cum_profit_data.iloc[row, column_peak]
            prev_peak = cum_profit_data.iloc[row - 1, column_peak]
            # Skip first row
            if row == 0:
                pass
            elif curr_profit > prev_peak:
                curr_peak = curr_profit
            else:
                curr_peak = prev_peak
            cum_profit_data.loc[cum_profit_data.index[row], 'Peak_' + symbol] = curr_peak
            curr_dd = (curr_profit - curr_peak)/curr_peak*100
            cum_profit_data.loc[cum_profit_data.index[row], 'DD%_' + symbol] = curr_dd

    #         # If previous profit is 0 then change is 0
    #         elif cum_profit_data.iloc[row - 1, column] == 0:
    #             cum_profit_data.loc[cum_profit_data.index[row], 'Change%_'+symbol] = 0
    #         else:
    #             # Change in %
    #             change = ((cum_profit_data.iloc[row, column] - cum_profit_data.iloc[row - 1][column]) / cum_profit_data.iloc[row - 1, column] * 100)
    #             # If new profit is higher the previous, change is positive, else is negative
    #             curr_profit = cum_profit_data.iloc[row , column]
    #             prev_profit = cum_profit_data.iloc[row - 1, column]
    #             if curr_profit > prev_profit:
    #                 change = abs(change)
    #             else:
    #                 change = -abs(change)
    #             cum_profit_data.loc[cum_profit_data.index[row], 'Change%_'+symbol] = change
    #
    # # Change for summary
    # column = cum_profit_data.columns.get_loc('Sum profit')
    #
    # # Pass each row- index
    # for row in number_of_days:
    #     # Skip first row (no previous profit)
    #     if row == 0:
    #         pass
    #     # If previous profit is 0 then change is 0
    #     elif cum_profit_data.iloc[row - 1, column] == 0:
    #         cum_profit_data.loc[cum_profit_data.index[row], 'Change%_sum'] = 0
    #     else:
    #         # Change in %
    #         change = ((cum_profit_data.iloc[row, column] - cum_profit_data.iloc[row - 1][column]) /
    #                   cum_profit_data.iloc[row - 1, column] * 100)
    #         # If new profit is higher the previous, change is positive, else is negative
    #         curr_profit = cum_profit_data.iloc[row, column]
    #         prev_profit = cum_profit_data.iloc[row - 1, column]
    #         if curr_profit > prev_profit:
    #             change = abs(change)
    #         else:
    #             change = -abs(change)
    #         cum_profit_data.loc[cum_profit_data.index[row], 'Change%_sum'] = change
    #
    #

    cum_profit_data = cum_profit_data.round(2)

    return cum_profit_data


if __name__ == '__main__':

    # backtest = backtest_atr_weight(symbols, test_period_y, atr_time_period, account)
    # backtest_summary(backtest)
    # print(backtest_summary(backtest))
    single_stock.calculate_change('AAPL', 3)

    # output = current_atr_weight(symbols, atr_time_period, initial_account)
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
