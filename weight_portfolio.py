# from datetime import date, timedelta
import pandas_datareader.data as pd_web
import pandas as pd


def data_download(symbol, download_begin, download_end, atr_period_days):
    # Function to download price data for symbol for specified date window
    # Usage: data_download('SPY', '2019-02-03', '2020-06-01')
    # Output [0]: all prices
    # Output [1]: close price with column name=symbol

    print('Loading ', symbol)
    df_all_prices = pd_web.DataReader(symbol, 'yahoo', download_begin, download_end)

    # If number of days is lower than ATR time period+1 (for calculation of ATR we need previous day close)
    # decrease begin date and load again
    # while len(df_all_prices.index) < (atr_period_days+1):
    #     # todo: typ pre begin/end a timedelta nesedi
    #     download_begin = download_begin - timedelta(days=1)
    #     df_all_prices = pd_web.DataReader(symbol, 'yahoo', download_begin, download_end)

    # Formating output
    df_all_prices = df_all_prices.round(2)
    df_close = pd.DataFrame()
    df_close[symbol+'_Close'] = df_all_prices['Close']

    return df_all_prices, df_close


def atr(symbol, df_all_prices, atr_period_days):
    # Function to calculate ATR on close prices for the period

    # New column: previous day close (pClose)
    df_all_prices['pClose'] = df_all_prices['Close'].shift(1)
    # New columns for formula
    df_all_prices['H-L'] = df_all_prices['High'] - df_all_prices['Low']
    df_all_prices['H-pClose'] = abs(df_all_prices['High'] - df_all_prices['pClose'])
    df_all_prices['L-pClose'] = abs(df_all_prices['Low'] - df_all_prices['pClose'])
    # Extract new columns
    df_true_range = df_all_prices[['H-L', 'H-pClose', 'L-pClose']].copy()
    # Calculating True Range- highest value of
    df_true_range['TR'] = df_true_range.max(axis=1, skipna=True)
    # Exponential moving average on True range- ATR
    # TODO: skontrolovat ci to dobre pocita EMA
    df_true_range['ATR'] = df_true_range['TR'].ewm(span=atr_period_days).mean().round(2)

    # Create output dataframe with ATR only
    df_atr = pd.DataFrame()
    df_atr[symbol+'_ATR'] = df_true_range['ATR']

    return df_atr


def weight(symbols, df_atr_all):
    # Calculation weight based on ATR, higher ATR is lower weight
    # Input: One row of data, ATR for each symbol
    # Output: One row of data, Weight for each symbol

    sum_atr = df_atr_all.sum(axis=1)

    for symbol in symbols:
        # Calculation weight, formula= (1-ATR/Sum of ATRs)/(number of symbols -1)
        df_atr_all[symbol+'_weight'] = ((1 - df_atr_all[symbol+'_ATR'] / sum_atr) / (len(symbols) - 1)).round(3)

    df_weight_all = df_atr_all.filter(regex='weight')
    return df_weight_all


def drawdown(symbol, df_cum_profit):
    # Calculate drawdown for one symbol
    # Input: symbol name, dataframe with cumulative profit
    # Output: dataframe with drawdown

    # We will work with copy of the input dataframe
    df_profit = df_cum_profit.copy()

    # Numbers of days in backtest period (index)
    number_of_days = range(0, len(df_profit.index))

    # Add new column Peak and Drawdown for each symbol, first row is 0
    df_profit[symbol + '_profit_peak'] = 0
    df_profit[symbol + '_DD%'] = 0

    # Peak in profit for symbol
    # Column- symbol
    column_profit = df_profit.columns.get_loc(symbol + '_cum_profit')
    column_peak = df_profit.columns.get_loc(symbol + '_profit_peak')
    # column_dd = df_profit.columns.get_loc(symbol + '_DD%')

    # Row- index
    for row in number_of_days:
        curr_profit = df_profit.iloc[row, column_profit]
        curr_peak = df_profit.iloc[row, column_peak]
        prev_peak = df_profit.iloc[row - 1, column_peak]
        # Skip first row
        if row == 0:
            pass
        elif curr_profit > prev_peak:
            curr_peak = curr_profit
        else:
            curr_peak = prev_peak
        df_profit.loc[df_profit.index[row], symbol + '_profit_peak'] = curr_peak

        if curr_peak == 0:
            curr_dd = 0
        else:
            curr_dd = (curr_profit - curr_peak) / curr_peak * 100
        df_profit.loc[df_profit.index[row], symbol + '_DD%'] = round(curr_dd, 2)

    df_dd = df_profit.filter(regex='DD')
    return df_dd
