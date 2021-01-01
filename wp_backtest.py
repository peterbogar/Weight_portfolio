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


def count_avg_price(fdiff, fclose_price, fshares, fprevious_shares, fprevious_avg_price):
    # Variables starts with F because of warning message
    # ak je dif vacsi ako nula
    # (cena * roziel + pred suma akci * pred avg cena) / nova suma akci
    # ak je rozdiel 0 alebo menej ako nula
    # predchadzjauca avg price
    if fdiff > 0:
        favg_price = ((fclose_price*fdiff)+(fprevious_shares*fprevious_avg_price))/fshares
        return favg_price
    else:
        return fprevious_avg_price


def count_profit(fdiff, fclose_price, favg_price):
    # Variables starts with F because of warning message
    # ak je rozdiel akci mensi ako nula
    # (avg cena-cena) * rozdiel
    # ak je rozdiel vacsi ako nula
    # 0
    if fdiff > 0:
        profit = (favg_price-fclose_price)*fdiff
        return profit
    else:
        return 0


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

# Added columns for previous shares number and difference in shares
for symbol in symbols:
    close_shares_selected_date_data['Prev sh_'+symbol] = close_shares_selected_date_data['Shares_'+symbol].shift(1)
    close_shares_selected_date_data['Diff sh_'+symbol] = close_shares_selected_date_data['Shares_'+symbol] - close_shares_selected_date_data['Prev sh_'+symbol]

# Create column for average price for each symbol
for symbol in symbols:
    close_shares_selected_date_data['Avg Close_'+symbol] = None

# First average price is close price for each symbol
for symbol in symbols:
    close_shares_selected_date_data.iloc[0, close_shares_selected_date_data.columns.get_loc('Avg Close_'+symbol)] = close_shares_selected_date_data.iloc[0, close_shares_selected_date_data.columns.get_loc('Close_'+symbol)]


number_of_days = range(0, len(close_shares_selected_date_data.index))

for symbol in symbols:
    for index in number_of_days:
        if index == 0:
            pass
        else:
            # Set variables for function 'count average price'
            diff = close_shares_selected_date_data.iloc[index, close_shares_selected_date_data.columns.get_loc('Diff sh_'+symbol)]
            close_price = close_shares_selected_date_data.iloc[index, close_shares_selected_date_data.columns.get_loc('Close_'+symbol)]
            shares = close_shares_selected_date_data.iloc[index, close_shares_selected_date_data.columns.get_loc('Shares_'+symbol)]
            previous_shares = close_shares_selected_date_data.iloc[index, close_shares_selected_date_data.columns.get_loc('Prev sh_'+symbol)]
            previous_avg_price = close_shares_selected_date_data.iloc[index-1, close_shares_selected_date_data.columns.get_loc('Avg Close_'+symbol)]

            # Count average price
            close_shares_selected_date_data.iloc[index, close_shares_selected_date_data.columns.get_loc('Avg Close_'+symbol)] = count_avg_price(diff, close_price, shares, previous_shares, previous_avg_price)

print(close_shares_selected_date_data)
