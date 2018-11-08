from back_test.model.base_option_set import BaseOptionSet
from back_test.model.base_account import BaseAccount
from back_test.model.base_instrument import BaseInstrument
import data_access.get_data as get_data
import back_test.model.constant as c
import datetime
import numpy as np
from Utilities.PlotUtil import PlotUtil
import matplotlib.pyplot as plt
import pandas as pd
from OptionStrategyLib.VolatilityModel.historical_volatility import HistoricalVolatilityModels as histvol
from OptionStrategyLib.OptionReplication.synthetic_option import SytheticOption
from back_test.model.trade import Order


def open_position(df_index, dt_date):
    if dt_date not in df_index.index:
        return False
    ma_5 = df_index.loc[dt_date, 'ma_5']
    ma_60 = df_index.loc[dt_date, 'ma_60']
    if ma_5 < ma_60:
        return True
    else:
        return False


def close_position(df_index, dt_date):
    ma_5 = df_index.loc[dt_date, 'ma_5']
    ma_60 = df_index.loc[dt_date, 'ma_60']
    if ma_5 > ma_60:
        return True
    else:
        return False


def execute(strategy_res, unit_index):
    for option in strategy_res.keys():
        if option is None:
            continue
        unit = unit_index / option.multiplier()
        order = account.create_trade_order(option, strategy_res[option], unit, cd_trade_price=cd_trade_price)
        record = option.execute_order(order, slippage=slippage)
        account.add_record(record, option)


start_date = datetime.date(2016, 1, 1)
end_date = datetime.date(2018, 11, 1)
dt_histvol = start_date - datetime.timedelta(days=500)
min_holding = 20
init_fund = c.Util.BILLION
slippage = 0
cd_trade_price = c.CdTradePrice.VOLUME_WEIGHTED
cd_hedge_price = c.CdTradePrice.CLOSE

name_code_option = c.Util.STR_50ETF
# df_metrics = get_data.get_50option_mktdata(start_date, end_date)
df_future_c1_daily = get_data.get_mktdata_future_c1_daily(start_date, end_date, c.Util.STR_IH)
df_futures_all_daily = get_data.get_mktdata_future_daily(start_date, end_date,
                                                         c.Util.STR_IH)  # daily data of all future contracts

df_index = get_data.get_index_mktdata(dt_histvol, end_date, c.Util.STR_INDEX_50ETF)
df_index['ma_5'] = c.Statistics.moving_average(df_index[c.Util.AMT_CLOSE], n=5).shift()
df_index['ma_60'] = c.Statistics.moving_average(df_index[c.Util.AMT_CLOSE], n=60).shift()
df_index['ma_120'] = c.Statistics.moving_average(df_index[c.Util.AMT_CLOSE], n=120).shift()
df_index['histvol_20'] = histvol.hist_vol(df_index[c.Util.AMT_CLOSE]).shift()

dt_start = max(df_future_c1_daily[c.Util.DT_DATE].values[0], df_index[c.Util.DT_DATE].values[0])
df_index = df_index[df_index[c.Util.DT_DATE] >= dt_start].reset_index(drop=True)
df_c1 = df_future_c1_daily[df_future_c1_daily[c.Util.DT_DATE] >= dt_start].reset_index(drop=True)
df_c_all = df_futures_all_daily[df_futures_all_daily[c.Util.DT_DATE] >= dt_start].reset_index(drop=True)
df_index1 = df_index.set_index(c.Util.DT_DATE)

index = BaseInstrument(df_index)
index.init()
hedging = SytheticOption(df_c1, frequency=c.FrequentType.DAILY, df_c1_daily=df_c1, df_futures_all_daily=df_c_all)
hedging.init()
account = BaseAccount(init_fund=c.Util.BILLION, leverage=1.0, rf=0.03)

# 标的指数开仓
unit_index = np.floor(account.cash / index.mktprice_close() / index.multiplier())
option_shares = unit_index
order_index = account.create_trade_order(index, c.LongShort.LONG, unit_index, cd_trade_price=c.CdTradePrice.CLOSE)
record_index = index.execute_order(order_index, slippage=slippage)
account.add_record(record_index, index)

df_holding_period = pd.DataFrame()
empty_position = True
unit_p = None
unit_c = None
id_future = hedging.current_state[c.Util.ID_FUTURE]
init_index = df_index[c.Util.AMT_CLOSE].values[0]
base_npv = []
while index.eval_date <= end_date:

    # # 标的移仓换月
    # if not empty_position and id_future != hedging.current_state[c.Util.ID_FUTURE]:
    #     for holding in account.dict_holding.values():
    #         if isinstance(holding, SytheticOption):
    #             df = hedging.df_all_futures_daily[
    #                 (hedging.df_all_futures_daily[c.Util.DT_DATE] == hedging.eval_date) & (
    #                     hedging.df_all_futures_daily[c.Util.ID_FUTURE] == id_future)]
    #             trade_unit = account.trade_book.loc[hedging.name_code(), c.Util.TRADE_UNIT]
    #             if account.trade_book.loc[hedging.name_code(), c.Util.TRADE_LONG_SHORT] == c.LongShort.LONG:
    #                 long_short = c.LongShort.SHORT
    #             else:
    #                 long_short = c.LongShort.LONG
    #             trade_price = df[c.Util.AMT_TRADING_VALUE].values[0] / df[c.Util.AMT_TRADING_VOLUME].values[
    #                 0] / hedging.multiplier()
    #             order = Order(holding.eval_date, hedging.name_code(), trade_unit, trade_price,
    #                           holding.eval_datetime, long_short)
    #             record = hedging.execute_order(order, slippage=slippage)
    #             account.add_record(record, holding)
    #     hedging.synthetic_unit = 0
    #     id_future = hedging.current_state[c.Util.ID_FUTURE]
    #     flag_hedge = True

    # 平仓
    if not empty_position:
        if close_position(df_index1, hedging.eval_date):
            for option in account.dict_holding.values():
                if isinstance(option, BaseInstrument):
                    continue
                else:
                    order = account.create_close_order(option, cd_trade_price=cd_trade_price)
                record = option.execute_order(order, slippage=slippage)
                account.add_record(record, option)
            empty_position = True

    # 开仓：距到期1M
    if empty_position and open_position(df_index1, hedging.eval_date):
        execute({hedging: c.LongShort.SHORT}, unit_index / 1000)
        empty_position = False


    if not hedging.has_next():
        close_out_orders = account.creat_close_out_order()
        for order in close_out_orders:
            execution_record = account.dict_holding[order.id_instrument].execute_order(order, slippage=0,
                                                                                       execute_type=c.ExecuteType.EXECUTE_ALL_UNITS)
            account.add_record(execution_record, account.dict_holding[order.id_instrument])
        account.daily_accounting(index.eval_date)
        base_npv.append(index.mktprice_close() / init_index)
        break
    account.daily_accounting(hedging.eval_date)
    base_npv.append(index.mktprice_close() / init_index)
    hedging.next()
    index.next()




account.account.to_csv('../../accounts_data/hedge_by_future_account.csv')
account.trade_records.to_csv('../../accounts_data/hedge_by_future_records.csv')
res = account.analysis()
print(res)
pu = PlotUtil()
dates = list(account.account.index)
hedged_npv = list(account.account[c.Util.PORTFOLIO_NPV])
pu.plot_line_chart(dates, [hedged_npv, base_npv], ['hedged_npv', 'base_npv'])

plt.show()
