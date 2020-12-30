# Vstup fnkcie bude zoznam symbolov, perioda v rokoch, perioda ATR v dnoch

import pandas as pd
from datetime import datetime, date, timedelta
import weight_portfolio

# Symbols to do backtest on
symbols = ['SPY', 'GLD']

# Time period in YEARS how long in history to do backtest,
# Last year is current- even if not finished yet
test_period_y = 1

# Time period in DAYS for ATR
atr_period = 20

account = 10000

current_year = date.today().year
test_begin = current_year - test_period_y + 1
test_end = current_year + 1

# Empty variables
collected_data = pd.DataFrame()
output_data = pd.DataFrame({'Date': []})
print()

# Download data and count ATR for each symbol
for symbol in symbols:
    downloaded_data = weight_portfolio.data_download_for_backtest(symbol, test_begin, test_end)
    atr_data = weight_portfolio.count_atr(downloaded_data, atr_period)

    collected_data['Close_'+symbol] = downloaded_data['Close']
    collected_data['ATR_'+symbol] = atr_data['ATR']

# Count ATR sum
collected_data['ATR_sum'] = collected_data.filter(regex='ATR').sum(axis=1)

# Count weight and shares number
for symbol in symbols:
    # Calculation weight, formula= (1-ATR/Sum of ATRs)/(number of symbols -1)
    collected_data['Weight_'+symbol] = ((1 - collected_data['ATR_'+symbol] / collected_data['ATR_sum']) / (len(symbols) - 1)).round(3)
    # Number of shares based on weight, current price and account
    collected_data['Shares_'+symbol] = (collected_data['Weight_'+symbol] * account / collected_data['Close_'+symbol]).round(2)

# Hide unnecessary columns
shares_data = collected_data.filter(regex='Close|Shares')

# Pick up one day in each month, create new dataframe with just Date-index
for y in range(test_begin, test_end):
    for m in range(1, 13):
        # Last day in month must be 28th because of February
        select_date = datetime(y, m, 28)

        # If selected date is weekend, decrease the date, check it 4x
        for i in [1, 2, 3, 4]:
            try:
                shares_data.loc[select_date]
            except KeyError:
                select_date = select_date - timedelta(days=1)
        output_data.loc[len(output_data.index)] = [select_date]
output_data = output_data.set_index('Date')

# Combine both dataframes, with all data and with just picked up days
combined_data = pd.merge(output_data, shares_data, how='left', on='Date')

print(combined_data)
