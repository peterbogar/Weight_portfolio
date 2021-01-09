import weight_portfolio
import pandas as pd
from datetime import timedelta, datetime

# List of symbols you want to use
symbols = ['SPY', 'GLD', 'XLE']

# Time period in days for ATR indicator
atr_period_days = 20

# Time period in years to backtest
backtest_period_years = 10

# Sum of account in USD
initial_account = 10000

df_atr_all = pd.DataFrame()

# Load data for each symbol and calculate ATR
for symbol in symbols:
    df_download = weight_portfolio.data_download(symbol, '2019-01-01', '2021-01-01', 20)
    df_atr = weight_portfolio.atr(symbol, df_download[0], 20)
    df_atr_all[symbol + '_ATR'] = df_atr[symbol + '_ATR']

df_weight_all = pd.DataFrame()

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

# Combine both dataframes, with all data and with just picked up days
df_some_weight = pd.merge(df_some_date, df_weight_all, how='left', on='Date')

df_some_weight['Account'] = 1000

print(df_some_weight)





#     # Number of shares based on weight, current price and account
#     close_atr_data_all['Shares'] = (close_atr_data_all['Weight'] * account / close_atr_data_all['Close']).round(2)
