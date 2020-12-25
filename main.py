# todo: vypisat datum za ktory mame data
# todo: vaha pre jeden symbol
# todo: translate to EN


import weight_portfolio
import pandas as pd

symbols = ['AAPL', 'SPY']
time_period = 10
account = 8000


if __name__ == '__main__':
    # Prazdny dataframe
    collected_data = pd.DataFrame({'Symbol': [], 'Close': [], 'ATR': [], 'Vaha': [], 'Pocet akci': []})

    # Nacitanie ceny a ATR pre kazdy symbol
    for symbol in symbols:
        downloaded_data = weight_portfolio.data_download(symbol=symbol, time_period=time_period)
        atr = weight_portfolio.count_atr(downloaded_data, atr_time_period=time_period)

        last_day = downloaded_data.index[-1]
        close_price = downloaded_data.iloc[-1][3]

        collected_data.loc[len(collected_data.index)] = [symbol, close_price, atr, 0, 0]

    # Nastav Symbol ako index
    collected_data = collected_data.set_index('Symbol')

    print(weight_portfolio.count_weight(collected_data=collected_data, account=account))
