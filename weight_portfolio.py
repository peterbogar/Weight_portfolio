from datetime import date, timedelta
import pandas_datareader.data as pd_web


def data_download(symbol, time_period_days):
    # Load market data from Yahoo for last X days for one symbol
    # Input: one symbol, time period in days.
    # Output: Dataframe with High, Low, Open, Close for each day in last time_period_days

    # Setup of today, begin, end
    today = date.today()
    # We dont need todays price, we need yeaterdays close price
    end = today - timedelta(days=1)
    begin = today - timedelta(days=(time_period_days + 1))

    # Data loading
    print('Loading ', symbol)
    downloaded_data = pd_web.DataReader(symbol, 'yahoo', begin, end)

    # If number of days is lower than time period+1 (for calculation of ATR we need previous day close
    # decrease begin date and load again
    while len(downloaded_data.index) < (time_period_days+1):
        begin = begin - timedelta(days=1)
        downloaded_data = pd_web.DataReader(symbol, 'yahoo', begin, end)

    # Dataframe format
    downloaded_data.reset_index(inplace=True)        # Set date as index
    downloaded_data.set_index("Date", inplace=True)
    downloaded_data = downloaded_data[['High', 'Low', 'Open', 'Close']]  # Cut off columns
    downloaded_data = downloaded_data.round(2)  # Round price

    # Output dataframe
    return downloaded_data


def count_atr(downloaded_data, atr_time_period):
    # Calculation of ATR for one symbol
    # Input: Dataframe with High, Low, Open, Close; ATR time period.
    # Output: Dataframe with close and ATR

    # Creating new column: previous day close (pClose)
    downloaded_data['pClose'] = downloaded_data['Close'].shift(1)
    # New columns for formula
    downloaded_data['H-L'] = downloaded_data['High'] - downloaded_data['Low']
    downloaded_data['H-pClose'] = abs(downloaded_data['High'] - downloaded_data['pClose'])
    downloaded_data['L-pClose'] = abs(downloaded_data['Low'] - downloaded_data['pClose'])
    # Copy of dataframe with new columns
    values_atr = downloaded_data[['H-L', 'H-pClose', 'L-pClose']].copy()
    # Calculating True Range- highest value of
    values_atr['TR'] = values_atr.max(axis=1, skipna=True)
    # Exponential moving average on True range- ATR
    # TODO: skontrolovat ci to dobre pocita EMA
    values_atr['ATR'] = values_atr['TR'].ewm(span=atr_time_period).mean().round(2)

    # Return last value of ATR
    # return values_atr.iloc[-1][-1]  # commented due to backtest

    # Create output dataframe with close price+ATR
    close_atr_data = downloaded_data[['Close']].copy()
    close_atr_data['ATR'] = values_atr['ATR']

    return close_atr_data


def count_weight_shares(close_atr_data_all, account):
    # Calculation weight based on ATR, higher ATR is lower weight
    # Input: Dataframe with prices and ATR for all symbols, account
    # Output: Dataframe with prices, ATR, weight, number of shares for all symbol

    sum_atr = close_atr_data_all['ATR'].sum()
    # Calculation weight, formula= (1-ATR/Sum of ATRs)/(number of symbols -1)
    close_atr_data_all['Weight'] = ((1 - close_atr_data_all['ATR'] / sum_atr) / (len(close_atr_data_all.index) - 1)).round(3)
    # Number of shares based on weight, current price and account
    close_atr_data_all['Shares'] = (close_atr_data_all['Weight'] * account / close_atr_data_all['Close']).round(2)

    symbol_close_atr_weight_shares_data = close_atr_data_all

    # Return dataframe with: Symbol, Price, ATR, Weight, Shares
    return symbol_close_atr_weight_shares_data


def data_download_for_backtest(symbol, begin, end):
    # Load market data from Yahoo.
    # Input: one symbol, start year, end year
    # Output: dataframe with current prices

    # Data loading
    print('Loading ', symbol)
    downloaded_data = pd_web.DataReader(symbol, 'yahoo', begin, end)

    # Dataframe format
    downloaded_data.reset_index(inplace=True)        # Set date as index
    downloaded_data.set_index("Date", inplace=True)
    downloaded_data = downloaded_data[['High', 'Low', 'Open', 'Close']]  # Cut off columns
    downloaded_data = downloaded_data.round(2)  # Round price

    # Dataframe with all prices
    return downloaded_data
