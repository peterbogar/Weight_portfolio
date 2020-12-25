from datetime import date, timedelta
import pandas_datareader.data as pd_web


def data_download(symbol, time_period):
    # Nacita data z Yahoo; vstup: jeden symbol, perioda; vystup: tabulka s datami

    # Definovanie dnesneho dna, zaciatku a konca
    today = date.today()
    # Nepocitame dnesny den, chceme vcerajsiu close cenu
    end = today - timedelta(days=1)
    # Ked nepocitame dnesny den, musime zaciatok posunut o jeden den dozadu
    begin = today - timedelta(days=(time_period + 1))
    # print()
    # print('Dnes: ', today)
    # print('Zaciatok: ', begin)
    # print('Koniec', end)
    # print()

    # Nacitanie dat
    print('Loading ', symbol)
    data_values = pd_web.DataReader(symbol, 'yahoo', begin, end)

    # Ak je pocet riadkov mensi ako time_period+1 (predchadzajuci close), posun zaciatok o jeden den dozadu
    while len(data_values.index) < (time_period+1):
        begin = begin - timedelta(days=1)
        data_values = pd_web.DataReader(symbol, 'yahoo', begin, end)

    # Formatovanie tabulky
    data_values.reset_index(inplace=True)        # Datum bude index
    data_values.set_index("Date", inplace=True)
    data_values = data_values[['High', 'Low', 'Open', 'Close']]  # Orezanie stlpcov
    data_values = data_values.round(2)  # zaokruhlenie ceny

    # Vrati Pandas dataframe s cenami
    return data_values


def count_atr(downloaded_data, atr_time_period):
    # Vypocet ATR, vstup: jeden symbol, perioda; vystup: posledna hodnota ATR

    # Nacitanie dat
    values = downloaded_data

    # Vytvorime novy stlpec- predchadzajuce Close (Cp)
    values['Cp'] = values['Close'].shift(1)
    # Nove stlpce pre pomocne vypocty
    values['H-L'] = values['High'] - values['Low']
    values['H-Cp'] = abs(values['High'] - values['Cp'])
    values['L-Cp'] = abs(values['Low'] - values['Cp'])
    # Musime skopirovat vypocitane stlpce do noveho dataframu
    values_atr = values[['H-L', 'H-Cp', 'L-Cp']].copy()
    # Najdeme najvacsiu hodnotu, to je True Range
    values_atr['TR'] = values_atr.max(axis=1, skipna=True)
    # Spravime EMA nad True Range, to je ATR
    values_atr['ATR'] = values_atr['TR'].ewm(span=atr_time_period).mean().round(2)

    # Vrati poslednu hodnotu ATR pre dany symbol
    return values_atr.iloc[-1][-1]


def count_weight(collected_data, account):
    # Vypocet vahy podla ATR, cim vacsie ATR, tym mensia vaha
    # Vstup: cena a ATR pre jeden symbol; vystup: doplni do tabulky vahu a pocet

    suma_atr = collected_data['ATR'].sum()
    # Vaha, vzorec: (1-ATR/Suma ATR)/(pocet riadkov-1)
    collected_data['Vaha'] = ((1 - collected_data['ATR'] / suma_atr) / (len(collected_data.index) - 1))
    #
    collected_data['Pocet akci'] = (collected_data['Vaha'] * account / collected_data['Close'])

    return collected_data
