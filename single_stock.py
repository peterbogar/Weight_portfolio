# Pre symbol vypocitat zmenu v % a max drawdown v %

import weight_portfolio
from datetime import date
import pandas as pd

def calculate_change(fsymbol, ftest_period_y):

    current_year = date.today().year
    test_begin = current_year - ftest_period_y
    test_end = current_year
    close_data = pd.DataFrame({fsymbol: []})

    downloaded_data = weight_portfolio.data_download_for_backtest(fsymbol, test_begin, test_end)
    close_data[fsymbol] = downloaded_data['Close'].copy()
    close_data[fsymbol+'_change%'] = 0

    number_of_days = range(0, len(close_data.index))
    for row in number_of_days:
        close_data.loc[close_data.index[row], fsymbol+'_change%'] = 1

    print(close_data)
