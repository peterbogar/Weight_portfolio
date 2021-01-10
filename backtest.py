import weight_portfolio
import pandas as pd
from datetime import timedelta, datetime

pd.set_option('display.max_columns', None)


# List of symbols you want to use
symbols = ['SPY', 'GLD']

# Time period in days for ATR indicator
atr_period_days = 20

# Time period in years to backtest
backtest_period_years = 2

# Initial account in USD
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


# Defining empty dataframes
df_atr_all = pd.DataFrame()
df_close_all = pd.DataFrame()
df_weight_all = pd.DataFrame()

download_end = datetime.today().year
download_begin = download_end - backtest_period_years

# Load data for each symbol and calculate ATR
for symbol in symbols:
    df_download = weight_portfolio.data_download(symbol, download_begin, download_end, atr_period_days)
    df_atr = weight_portfolio.atr(symbol, df_download[0], atr_period_days)
    df_atr_all[symbol + '_ATR'] = df_atr[symbol + '_ATR']
    df_close = df_download[1]
    df_close_all[symbol + '_Close'] = df_close[symbol+'_Close']
# df_atr_all.to_excel('atr_all.xls')
# df_close_all.to_excel('close_all.xls')

# Calculate weight for each symbol
for row in range(0, len(df_atr_all.index)):
    temp1 = df_atr_all.iloc[row]
    temp2 = pd.DataFrame(temp1).transpose()
    df_weight_all = df_weight_all.append(weight_portfolio.weight(symbols, temp2))
# df_weight_all.to_excel('weight_all.xls')

# Time period for rebalancing, currently once a month
# Pick up one day in each month, create new dataframe with just Date-index
# TODO: prerobit na modifikovatelne
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

# Combine some_date dataframe and close price dataframe
df_some_price = pd.merge(df_some_date, df_close_all, how='left', on='Date')
# Combine this dataframe with weight dataframe
df_some_weight = pd.merge(df_some_price, df_weight_all, how='left', on='Date')

# Rename dataframe
df_output = df_some_weight

# Set empty columns
df_output['Account'] = initial_account
for symbol in symbols:
    df_output[symbol+'_shares'] = 0
    df_output[symbol+'_shares_diff'] = 0
    df_output[symbol+'_avg_price'] = 0
    df_output[symbol+'_profit'] = 0
    df_output[symbol + '_cum_profit'] = 0
df_output['Sum_profit'] = 0
df_output['Sum_cum_profit'] = 0

# Set first shares and avg price for each symbol
for symbol in symbols:
    first_close = df_output.iloc[0, df_output.columns.get_loc(symbol+'_Close')]
    first_weight = df_output.iloc[0, df_output.columns.get_loc(symbol+'_weight')]
    first_account = df_output.iloc[0, df_output.columns.get_loc('Account')]
    df_output.iloc[0, df_output.columns.get_loc(symbol+'_shares')] = (first_account * first_weight / first_close).round(0)
    df_output.iloc[0, df_output.columns.get_loc(symbol + '_avg_price')] = first_close

# Numbers of days in backtest period (index)
number_of_days = range(0, len(df_output.index))

# Row by row
#   symbol by symbol - calculate account, shares, avg price, profit, sum profit for each symbol
for row in number_of_days:
    sum_profit = 0
    for symbol in symbols:
        row_close = df_output.iloc[row, df_output.columns.get_loc(symbol+'_Close')]
        row_weight = df_output.iloc[row, df_output.columns.get_loc(symbol+'_weight')]
        row_account = df_output.iloc[row, df_output.columns.get_loc('Account')]
        row_shares = (row_account * row_weight / row_close).round(0)
        row_prev_shares = df_output.iloc[row-1, df_output.columns.get_loc(symbol+'_shares')]
        row_shares_diff = row_shares - row_prev_shares
        row_prev_avg_price = df_output.iloc[row-1, df_output.columns.get_loc(symbol+'_avg_price')]
        row_avg_price = round(avg_price(row_shares_diff, row_close, row_shares, row_prev_shares, row_prev_avg_price), 2)
        row_profit = profit(row_shares_diff, row_close, row_avg_price)
        df_output.iloc[row, df_output.columns.get_loc(symbol+'_shares')] = row_shares
        df_output.iloc[row, df_output.columns.get_loc(symbol + '_shares_diff')] = row_shares_diff
        df_output.iloc[row, df_output.columns.get_loc(symbol + '_avg_price')] = row_avg_price
        df_output.iloc[row, df_output.columns.get_loc(symbol + '_profit')] = row_profit
        sum_profit += row_profit
        row_new_accouont = df_output.iloc[row-1, df_output.columns.get_loc('Account')] + sum_profit
        df_output.iloc[row, df_output.columns.get_loc('Account')] = row_new_accouont
    df_output.iloc[row, df_output.columns.get_loc('Sum_profit')] = sum_profit

# Calculate cumulative profit for each symbol
for symbol in symbols:
    df_output[symbol+'_cum_profit'] = df_output[symbol+'_profit'].cumsum()

# Calculate cumulative summary profit
df_output['Sum_cum_profit'] = df_output['Sum_profit'].cumsum()

# Drawdown for each symbol and Summary too
symbols = symbols + ['Sum']
for symbol in symbols:
    df_cum_profit = df_output.filter(regex=symbol+'_cum_profit')
    df_dd = weight_portfolio.drawdown(symbol, df_cum_profit)
    df_output = pd.merge(df_output, df_dd, how='left', on='Date')

print(df_output)
