import pandas as pd
# from datetime import date, datetime, timedelta
# import weight_portfolio
# import single_stock
# import backtest

# Display all columns in pandas dataframe
pd.set_option('display.max_columns', None)


# List of symbols you want to use
symbols = ['SPY', 'GLD', 'XLE']

# Time period in days for ATR indicator
atr_period_days = 20

# Time period in years to backtest
backtest_period_years = 10

# Sum of account in USD
initial_account = 10000


def main():
    pass



#     # Count cumulative profit for each symbol
#     for symbol in symbols:
#         df['Cum_profit_'+symbol] = df['Profit_'+symbol].cumsum()
#
#     # Change dataframe name
#     close_atr_weight_shares_selected_cumprofit_data = df
#
#     return close_atr_weight_shares_selected_cumprofit_data
# def backtest_summary(fdata):
#     # Summarize cumulative profit among all symbols
#     cum_profit_data = fdata.filter(regex='Cum').copy()
#     cum_profit_data['Sum profit'] = cum_profit_data.sum(axis=1)
#
#     # Numbers of days for backtest (index)
#     number_of_days = range(0, len(cum_profit_data.index))
#
#     # Add new column Peak and Drawdown for each symbol, first row is 0
#     for symbol in symbols:
#         cum_profit_data.loc[cum_profit_data.index[0], 'Peak_'+symbol] = 0
#         cum_profit_data.loc[cum_profit_data.index[0], 'DD%_' + symbol] = 0
#
#     # Peak in profit for symbols
#     for symbol in symbols:
#         # Column- symbol
#         column_profit = cum_profit_data.columns.get_loc('Cum_profit_'+symbol)
#         column_peak = cum_profit_data.columns.get_loc('Peak_'+symbol)
#         column_dd = cum_profit_data.columns.get_loc('DD%_'+symbol)
#
#         # Row- index
#         for row in number_of_days:
#             curr_profit = cum_profit_data.iloc[row, column_profit]
#             curr_peak = cum_profit_data.iloc[row, column_peak]
#             prev_peak = cum_profit_data.iloc[row - 1, column_peak]
#             # Skip first row
#             if row == 0:
#                 pass
#             elif curr_profit > prev_peak:
#                 curr_peak = curr_profit
#             else:
#                 curr_peak = prev_peak
#             cum_profit_data.loc[cum_profit_data.index[row], 'Peak_' + symbol] = curr_peak
#             curr_dd = (curr_profit - curr_peak)/curr_peak*100
#             cum_profit_data.loc[cum_profit_data.index[row], 'DD%_' + symbol] = curr_dd
#
#     #         # If previous profit is 0 then change is 0
#     #         elif cum_profit_data.iloc[row - 1, column] == 0:
#     #             cum_profit_data.loc[cum_profit_data.index[row], 'Change%_'+symbol] = 0
#     #         else:
#     #             # Change in %
#     #             change = ((cum_profit_data.iloc[row, column] - cum_profit_data.iloc[row - 1][column]) / cum_profit_data.iloc[row - 1, column] * 100)
#     #             # If new profit is higher the previous, change is positive, else is negative
#     #             curr_profit = cum_profit_data.iloc[row , column]
#     #             prev_profit = cum_profit_data.iloc[row - 1, column]
#     #             if curr_profit > prev_profit:
#     #                 change = abs(change)
#     #             else:
#     #                 change = -abs(change)
#     #             cum_profit_data.loc[cum_profit_data.index[row], 'Change%_'+symbol] = change
#     #
#     # # Change for summary
#     # column = cum_profit_data.columns.get_loc('Sum profit')
#     #
#     # # Pass each row- index
#     # for row in number_of_days:
#     #     # Skip first row (no previous profit)
#     #     if row == 0:
#     #         pass
#     #     # If previous profit is 0 then change is 0
#     #     elif cum_profit_data.iloc[row - 1, column] == 0:
#     #         cum_profit_data.loc[cum_profit_data.index[row], 'Change%_sum'] = 0
#     #     else:
#     #         # Change in %
#     #         change = ((cum_profit_data.iloc[row, column] - cum_profit_data.iloc[row - 1][column]) /
#     #                   cum_profit_data.iloc[row - 1, column] * 100)
#     #         # If new profit is higher the previous, change is positive, else is negative
#     #         curr_profit = cum_profit_data.iloc[row, column]
#     #         prev_profit = cum_profit_data.iloc[row - 1, column]
#     #         if curr_profit > prev_profit:
#     #             change = abs(change)
#     #         else:
#     #             change = -abs(change)
#     #         cum_profit_data.loc[cum_profit_data.index[row], 'Change%_sum'] = change
#     #
#     #
#
#     cum_profit_data = cum_profit_data.round(2)
#
#     return cum_profit_data


if __name__ == '__main__':
    main()
