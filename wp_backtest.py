# Vstup fnkcie bude zoznam symbolov a perioda v rokoch, perioda ATR
# nacita CSV pre kazdy symbol za dany pocet rokov
# Z tohto CSV bude potom vyberat hodnoty raz za mesiac za dany pocet dni- prerioda ATR
# novy pocet akci porovna so starym, a vypocita zisk
# vystup bude tabulka- jeden riadok-jeden mesiacx pocet , kde bude cena

import pandas as pd
import pandas_datareader as pd_web
from datetime import date, timedelta

symbols = ['SPY', 'GLD']
test_period_y = 10
atr_period = 20

current_year = date.today().year
test_begin = current_year - test_period_y + 1
test_end = current_year + 1

data_all = pd.DataFrame()
each_month = []

print()
print(current_year)
print(test_begin)
print(test_end)

# for symbol in symbols:
#     print('Loading ', symbol)
#     data = pd_web.DataReader(symbol, 'yahoo', test_begin, test_end)
#     data_all[symbol] = data['Adj Close']
# print(data_all)


for i in [1, 2, 3, 4, 5]:
    part_today = date(2019, 4, i)
    part_end = part_today
    part_begin = part_today - timedelta(days=atr_period)

