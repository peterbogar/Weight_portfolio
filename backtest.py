import weight_portfolio
import pandas as pd
from datetime import timedelta, datetime

pd.set_option('display.max_columns', None)

# List of symbols you want to use
symbols = ['SPY', 'GLD']

# Time period in days for ATR indicator
atr_period_days = 20

# Time period in years to backtest
backtest_period_years = 10

# Sum of account in USD
initial_account = 10000


def avg_price(shares_diff, close_price, shares, prev_shares, prev_avg_price):
    # Funkicia pocita average cenu
    # ak je rozdiel vacsi ako nula
    # (cena * roziel + pred suma akci * pred avg cena) / nova suma akci
    # ak je rozdiel 0 alebo menej plati predchadzajuca avg price
    if shares_diff > 0:
        new_avg_price = ((close_price*shares_diff)+(prev_shares*prev_avg_price))/shares
        return new_avg_price
    else:
        return prev_avg_price


def profit(shares_diff, close_price, new_avg_price):
    # Funkcia pocita profit
    # ak je rozdiel akci mensi ako nula
    # (avg cena-cena) * rozdiel
    # ak je rozdiel vacsi ako nula
    # 0
    if shares_diff < 0:
        new_profit = round((new_avg_price-close_price)*shares_diff, 2)
        return new_profit
    else:
        return 0


df_atr_all = pd.DataFrame()
df_close_all = pd.DataFrame()
df_weight_all = pd.DataFrame()

# Load data for each symbol and calculate ATR
for symbol in symbols:
    df_download = weight_portfolio.data_download(symbol, '2019-01-01', '2021-01-01', 20)
    df_atr = weight_portfolio.atr(symbol, df_download[0], 20)
    df_atr_all[symbol + '_ATR'] = df_atr[symbol + '_ATR']
    df_close = df_download[1]
    df_close_all[symbol + '_Close'] = df_close[symbol+'_Close']

# Calculate weight for each symbol
for row in range(0, len(df_atr_all.index)):
    a = df_atr_all.iloc[row]
    b = pd.DataFrame(a).transpose()
    df_weight_all = df_weight_all.append(weight_portfolio.weight(symbols, b))


# TODO: prerobit na modifikovatelne
# Time period for rebalancing, currently once a month
# Pick up one day in each month, create new dataframe with just Date-index
df_some_date = pd.DataFrame({'Date': []})
for y in range(2019, 2021):
    for m in range(1, 13):
        # Last day in month must be 28th because of February
        select_date = datetime(y, m, 28)

        # If selected date is weekend, decrease the date, check it 4x
        for _ in [1, 2, 3, 4]:
            try:
                df_weight_all.loc[select_date]
            except KeyError:
                select_date = select_date - timedelta(days=1)
        df_some_date.loc[len(df_some_date.index)] = [select_date]

# Set index
df_some_date = df_some_date.set_index('Date')
df_weight_all.index.name = 'Date'

# Combine some date dataframe and close price dataframe
df_some_price = pd.merge(df_some_date, df_close_all, how='left', on='Date')
# Combine this dataframe with weight dataframe
df_some_weight = pd.merge(df_some_price, df_weight_all, how='left', on='Date')

# Rename dataframe
df_output = df_some_weight

# Set empty columns
df_output['Account'] = 10000

for symbol in symbols:
    df_output[symbol+'_shares'] = 0
    # df_output[symbol+'_prev shares'] = 0
    df_output[symbol+'_shares diff'] = 0
    df_output[symbol+'_avg price'] = 0
    df_output[symbol+'_profit'] = 0

df_output['Sum profit'] = 0


# Set first two account value, in first step we dont have any profit yet, so also next account will be initial
df_output.iloc[0, df_output.columns.get_loc('Account')] = 10000
df_output.iloc[1, df_output.columns.get_loc('Account')] = 10000

# Set first shares and avg price for each symbol
for symbol in symbols:
    first_close = df_output.iloc[0, df_output.columns.get_loc(symbol+'_Close')]
    first_weight = df_output.iloc[0, df_output.columns.get_loc(symbol+'_weight')]
    first_account = df_output.iloc[0, df_output.columns.get_loc('Account')]
    df_output.iloc[0, df_output.columns.get_loc(symbol+'_shares')] = (first_account * first_weight / first_close).round(0)
    df_output.iloc[0, df_output.columns.get_loc(symbol + '_avg price')] = first_close


# Numbers of days for backtest (index)
number_of_days = range(0, len(df_output.index))

# Row by row
#   symbol by symbol - calculate account, shares, avg price, profit, cum profit for each symbol
for row in number_of_days:
    sum_profit = 0
    for symbol in symbols:
        row_close = df_output.iloc[row, df_output.columns.get_loc(symbol+'_Close')]
        row_weight = df_output.iloc[row, df_output.columns.get_loc(symbol+'_weight')]
        row_account = df_output.iloc[row, df_output.columns.get_loc('Account')]
        row_shares = (row_account * row_weight / row_close).round(0)
        row_prev_shares = df_output.iloc[row-1, df_output.columns.get_loc(symbol+'_shares')]
        row_shares_diff = row_shares - row_prev_shares
        row_prev_avg_price = df_output.iloc[row-1, df_output.columns.get_loc(symbol+'_avg price')]
        row_avg_price = round(avg_price(row_shares_diff, row_close, row_shares, row_prev_shares, row_prev_avg_price), 2)
        row_profit = profit(row_shares_diff, row_close, row_avg_price)
        df_output.iloc[row, df_output.columns.get_loc(symbol+'_shares')] = row_shares
        # df_output.iloc[row, df_output.columns.get_loc(symbol + '_prev shares')] = row_prev_shares
        df_output.iloc[row, df_output.columns.get_loc(symbol + '_shares diff')] = row_shares_diff
        df_output.iloc[row, df_output.columns.get_loc(symbol + '_avg price')] = row_avg_price
        df_output.iloc[row, df_output.columns.get_loc(symbol + '_profit')] = row_profit
        sum_profit += row_profit
        row_new_accouont = df_output.iloc[row-1, df_output.columns.get_loc('Account')] + sum_profit
        df_output.iloc[row, df_output.columns.get_loc('Account')] = row_new_accouont
    df_output.iloc[row, df_output.columns.get_loc('Sum profit')] = sum_profit



print(df_output)



# # How many rebalancing are in the testing period
# number_of_days = range(0, len(df.index))
#
# # For each symbol count average price and profit in separate functions
# for symbol in symbols:
#     for index in number_of_days:
#         if index == 0:
#             pass
#         else:
#             # Set variables for function 'count average price' and 'count profit'
#             diff = df.iloc[index, df.columns.get_loc('Diff shares' + symbol)]
#             close_price = df.iloc[index, df.columns.get_loc('Close_' + symbol)]
#             shares = df.iloc[index, df.columns.get_loc('Shares_' + symbol)]
#             previous_shares = df.iloc[index, df.columns.get_loc('Prev shares' + symbol)]
#             previous_avg_price = df.iloc[index - 1, df.columns.get_loc('Avg price_' + symbol)]
#
#             # Count average price in function
#             df.iloc[index, df.columns.get_loc('Avg price_' + symbol)] = weight_portfolio.count_avg_price_for_backtest(diff, close_price, shares, previous_shares, previous_avg_price)
#
#             # Count profit in function
#             avg_price = df.iloc[index, df.columns.get_loc('Avg price_' + symbol)]
#             df.iloc[index, df.columns.get_loc('Profit_' + symbol)] = weight_portfolio.count_profit_for_backtest(diff, close_price, avg_price)
