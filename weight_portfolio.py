from datetime import date, timedelta
import pandas_datareader.data as pd_web


def data_download(symbol, time_period):
    # Load market data from Yahoo.
    # Input: one symbol, time period.
    # Output: dataframe with current prices

    # Setup of today, begin, end
    today = date.today()
    # We dont need todays price, we need yeaterdays close price
    end = today - timedelta(days=1)
    begin = today - timedelta(days=(time_period + 1))

    # Data loading
    print('Loading ', symbol)
    data_values = pd_web.DataReader(symbol, 'yahoo', begin, end)

    # If number of days is lower than time period+1 (for calculation of ATR we need previous day close
    # decrease begin date and load again
    while len(data_values.index) < (time_period+1):
        begin = begin - timedelta(days=1)
        data_values = pd_web.DataReader(symbol, 'yahoo', begin, end)

    # Dataframe format
    data_values.reset_index(inplace=True)        # Set date as index
    data_values.set_index("Date", inplace=True)
    data_values = data_values[['High', 'Low', 'Open', 'Close']]  # Cut off columns
    data_values = data_values.round(2)  # Round price

    # Dataframe with all prices
    return data_values


def count_atr(downloaded_data, atr_time_period):
    # Calculation of ATR.
    # Input: Dataframe with prices, time period.
    # Output: Current ATR

    # Loading prices
    values = downloaded_data

    # Creating new column- previous day close (Cp)
    values['Cp'] = values['Close'].shift(1)
    # New columns for formula
    values['H-L'] = values['High'] - values['Low']
    values['H-Cp'] = abs(values['High'] - values['Cp'])
    values['L-Cp'] = abs(values['Low'] - values['Cp'])
    # Copy of dataframe with new columns
    values_atr = values[['H-L', 'H-Cp', 'L-Cp']].copy()
    # Calculating True Range- highest value of
    values_atr['TR'] = values_atr.max(axis=1, skipna=True)
    # Exponential moving average on True range- ATR
    values_atr['ATR'] = values_atr['TR'].ewm(span=atr_time_period).mean().round(2)

    # Return value of ATR
    return values_atr.iloc[-1][-1]  # commented due to backtest
    # return values_atr


def count_weight(collected_data, account):
    # Calculation weight based on ATR, higher ATR is lower weight
    # Input: Dataframe with price and ATR, account
    # Output: Dataframe with price, ATR, weight, number of shares for each symbol

    suma_atr = collected_data['ATR'].sum()
    # Calculation weight, formula= (1-ATR/Sum of ATRs)/(number of symbols -1)
    collected_data['Weight'] = ((1 - collected_data['ATR'] / suma_atr) / (len(collected_data.index) - 1)).round(3)
    # Number of shares based on weight, current price and account
    collected_data['Shares'] = (collected_data['Weight'] * account / collected_data['Close']).round(2)

    # Return dataframe with: Symbo, Price, ATR, Weight, Shares
    return collected_data


def data_download_for_backtest(symbol, begin, end):
    # Load market data from Yahoo.
    # Input: one symbol, start year, end year
    # Output: dataframe with current prices

    # Data loading
    print('Loading ', symbol)
    data_values = pd_web.DataReader(symbol, 'yahoo', begin, end)

    # Dataframe format
    data_values.reset_index(inplace=True)        # Set date as index
    data_values.set_index("Date", inplace=True)
    data_values = data_values[['High', 'Low', 'Open', 'Close']]  # Cut off columns
    data_values = data_values.round(2)  # Round price

    # Dataframe with all prices
    return data_values
