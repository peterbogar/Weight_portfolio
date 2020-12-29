# Vstup fnkcie bude zoznam symbolov a perioda v rokoch, perioda ATR
# nacita CSV pre kazdy symbol za dany pocet rokov
# Z tohto CSV bude potom vyberat hodnoty raz za mesiac za dany pocet dni- prerioda ATR
# novy pocet akci porovna so starym, a vypocita zisk
# vystup bude tabulka- jeden riadok-jeden mesiacx pocet , kde bude cena

import pandas as pd
import pandas_datareader as pd_web
from datetime import date, datetime, timedelta

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

# Empty variables
data_all = pd.DataFrame()

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
    # Load data for each symbol in the list
    print('Loading ', symbol)
    data = pd_web.DataReader(symbol, 'yahoo', test_begin, test_end)
    data_all[symbol] = data['Adj Close']

# cyklus for pre kazdy symbol
#   nacitat x rokov
#   v cykle pre kazdy mesiac, nacitat
#       vypocet atr, vaha, pocet
#       vystup: nova tabulka- kazdy mesiac: cena, pocet akcii
#   doplnit do dalsie stlpce do existujucej tabulky
