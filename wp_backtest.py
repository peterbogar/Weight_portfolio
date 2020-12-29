# Vstup fnkcie bude zoznam symbolov a perioda v rokoch, perioda ATR
# nacita CSV pre kazdy symbol za dany pocet rokov
# Z tohto CSV bude potom vyberat hodnoty raz za mesiac za dany pocet dni- prerioda ATR
# novy pocet akci porovna so starym, a vypocita zisk
# vystup bude tabulka- jeden riadok-jeden mesiacx pocet , kde bude cena

import pandas as pd
import pandas_datareader as pd_web
from datetime import date, timedelta

# Symbols to do backtest on
symbols = ['SPY', 'GLD']
# Time period in YEARS how long in history to do backtest,
# Last year is current- even if not finished yet
test_period_y = 2
# Time period in DAYS for ATR
atr_period = 20

current_year = date.today().year
test_begin = current_year - test_period_y + 1
test_end = current_year + 1

data_all = pd.DataFrame()

print()

# for symbol in symbols:
#     print('Loading ', symbol)
#     data = pd_web.DataReader(symbol, 'yahoo', test_begin, test_end)
#     data_all[symbol] = data['Adj Close']
# print(data_all)

for y in range(test_begin, test_end):
    for m in range(1, 13):
        part_today = date(y, m, 1)
        print(part_today)
