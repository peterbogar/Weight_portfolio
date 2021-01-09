# from datetime import date, timedelta
import pandas_datareader.data as pd_web
import pandas as pd


# def count_avg_price_for_backtest(fdiff, fclose_price, fshares, fprevious_shares, fprevious_avg_price):
#     # Funkicia pocita average cenu
#     # Variables starts with F because of warning message
#     # ak je dif vacsi ako nula
#     # (cena * roziel + pred suma akci * pred avg cena) / nova suma akci
#     # ak je rozdiel 0 alebo menej ako nula
#     # predchadzjauca avg price
#     if fdiff > 0:
#         favg_price = ((fclose_price*fdiff)+(fprevious_shares*fprevious_avg_price))/fshares
#         return favg_price
#     else:
#         return fprevious_avg_price
# def count_profit_for_backtest(fdiff, fclose_price, favg_price):
#     # Funkcia pocita profit
#     # Variables starts with F because of warning message
#     # ak je rozdiel akci mensi ako nula
#     # (avg cena-cena) * rozdiel
#     # ak je rozdiel vacsi ako nula
#     # 0
#     if fdiff < 0:
#         profit = round((favg_price-fclose_price)*fdiff, 2)
#         return profit
#     else:
#         return 0


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


def shares():

    pass


def profit():
    pass


def drawdown():
    pass
