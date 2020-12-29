# Vstup fnkcie bude zoznam symbolov a perioda v rokoch, perioda ATR v dnoch
# novy pocet akci porovna so starym, a vypocita zisk
# vystup bude tabulka- jeden riadok-jeden mesiacx pocet , kde bude cena

import pandas as pd
# import pandas_datareader as pd_web
from datetime import date
import weight_portfolio

# Symbols to do backtest on
symbols = ['SPY', 'GLD', 'AAPL']
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
data_all = pd.DataFrame()
collected_data = pd.DataFrame()

print()

# for y in range(test_begin, test_end):
#     for m in range(1, 13):
#         # Last day in month must be 28th because of February
#         select_date = datetime(y, m, 28)
#
#         # If selected date is weekend, decrease the date- check it 3x
#         for i in [1, 2, 3, 4]:
#             try:
#                 data_all.loc[select_date]
#             except KeyError:
#                 select_date = select_date - timedelta(days=1)
#         # print(select_date)

for symbol in symbols:
    downloaded_data = weight_portfolio.data_download_for_backtest(symbol, test_begin, test_end)
    atr_data = weight_portfolio.count_atr(downloaded_data, atr_period)

    collected_data['Close_'+symbol] = downloaded_data['Close']
    collected_data['ATR_'+symbol] = atr_data['ATR']

collected_data['ATR_sum'] = collected_data.filter(regex='ATR').sum(axis=1)

for symbol in symbols:
    # Calculation weight, formula= (1-ATR/Sum of ATRs)/(number of symbols -1)
    collected_data['Weight_'+symbol] = ((1 - collected_data['ATR_'+symbol] / collected_data['ATR_sum']) / (len(symbols) - 1)).round(3)
    # Number of shares based on weight, current price and account
    collected_data['Shares_'+symbol] = (collected_data['Weight_'+symbol] * account / collected_data['Close_'+symbol]).round(0)


output_data = collected_data.filter(regex='Close|Shares')
print(output_data)

# for y in range(test_begin, test_end):
#     for m in range(1, 13):
#         # Last day in month must be 28th because of February
#         select_date = datetime(y, m, 28)
#
#         # If selected date is weekend, decrease the date, check it 4x
#         for i in [1, 2, 3, 4]:
#             try:
#                 downloaded_data.loc[select_date]
#             except KeyError:
#                 select_date = select_date - timedelta(days=1)
#         # print(select_date)
