# Vstup fnkcie bude zoznam symbolov, perioda v rokoch, perioda ATR v dnoch

import pandas as pd
from datetime import datetime, date, timedelta
import weight_portfolio

# Symbols to do backtest on
symbols = ['SPY', 'GLD']

# Time period in YEARS how long in history to do backtest
# Last year is current- even if not finished yet
test_period_y = 1

# Time period in DAYS for ATR
atr_period = 20

account = 10000

current_year = date.today().year
test_begin = current_year - test_period_y
test_end = current_year

# Display all columns in pandas dataframe
pd.set_option('display.max_columns', None)

# Empty variables
close_atr_data = pd.DataFrame()
selecet_date_data = pd.DataFrame({'Date': []})
print()

# Download data and count ATR for each symbol
for symbol in symbols:
    downloaded_data = weight_portfolio.data_download_for_backtest(symbol, test_begin, test_end)
    atr_data = weight_portfolio.count_atr(downloaded_data, atr_period)

    close_atr_data['Close_' + symbol] = downloaded_data['Close']
    close_atr_data['ATR_' + symbol] = atr_data['ATR']

# Count ATR sum
close_atr_data['ATR_sum'] = close_atr_data.filter(regex='ATR').sum(axis=1)

# Count weight and shares number
for symbol in symbols:
    # Calculation weight, formula= (1-ATR/Sum of ATRs)/(number of symbols -1)
    close_atr_data['Weight_' + symbol] = ((1 - close_atr_data['ATR_' + symbol] / close_atr_data['ATR_sum']) / (len(symbols) - 1)).round(3)
    # Number of shares based on weight, current price and account
    # zaokruhkenie je matematicke, nie na nmensie cislo
    close_atr_data['Shares_' + symbol] = (close_atr_data['Weight_' + symbol] * account / close_atr_data['Close_' + symbol]).round(0)

# Hide unnecessary columns
close_shares_data = close_atr_data.filter(regex='Close|Shares')

# Pick up one day in each month, create new dataframe with just Date-index
for y in range(test_begin, test_end):
    for m in range(1, 13):
        # Last day in month must be 28th because of February
        select_date = datetime(y, m, 28)

        # If selected date is weekend, decrease the date, check it 4x
        for i in [1, 2, 3, 4]:
            try:
                close_shares_data.loc[select_date]
            except KeyError:
                select_date = select_date - timedelta(days=1)
        selecet_date_data.loc[len(selecet_date_data.index)] = [select_date]
selecet_date_data = selecet_date_data.set_index('Date')

# Combine both dataframes, with all data and with just picked up days
close_shares_selected_date_data = pd.merge(selecet_date_data, close_shares_data, how='left', on='Date')

# Added columns for previous shares number and diferenc in shares
for symbol in symbols:
    close_shares_selected_date_data['Prev sh_'+symbol] = close_shares_selected_date_data['Shares_'+symbol].shift(1)
    close_shares_selected_date_data['Dif sh_'+symbol] = close_shares_selected_date_data['Shares_'+symbol] - close_shares_selected_date_data['Prev sh_'+symbol]


for symbol in symbols:
    close_shares_selected_date_data['Avg Close_'+symbol] = None


print(close_shares_selected_date_data)
print()

# symbol = 'SPY'
# print(len(close_shares_selected_date_data.index))
# print(close_shares_selected_date_data.iloc[-1]['Close_'+symbol])
# print(close_shares_selected_date_data.iloc[-1]['Shares_'+symbol])
