from back_test.model.base_option_set import BaseOptionSet
from back_test.model.base_instrument import BaseInstrument
from back_test.model.base_option import BaseOption
from back_test.model.base_account import BaseAccount
import data_access.get_data as get_data
import back_test.model.constant as c
import datetime
import numpy as np
from OptionStrategyLib.OptionReplication.synthetic_option import SytheticOption
from Utilities.PlotUtil import PlotUtil
import matplotlib.pyplot as plt
import pandas as pd
from Utilities.timebase import LLKSR, KALMAN, LLT
from back_test.model.trade import Order


def select_target_moneyness_put(cd_call_put,optionset,moneyness,maturity):
    list_call_mdt, list_put_mdt = optionset.get_options_list_by_moneyness_mthd1(moneyness_rank=moneyness,
                                                                                  maturity=maturity)
    put = optionset.select_higher_volume(list_put_mdt)
    if put is None:
        put = optionset.select_higher_volume(optionset.get_deepest_otm_put_list(maturity))
    return put

def close_option_position(account):
    for option in account.dict_holding.values():
        if not isinstance(option, BaseOption): continue
        order = account.create_close_order(option, cd_trade_price=cd_price)
        record = option.execute_order(order, slippage=slippage)
        account.add_record(record, option)
    return True

pu = PlotUtil()
start_date = datetime.date(2015, 2, 9)
end_date = datetime.date(2019,1,7)
dt_histvol = start_date - datetime.timedelta(days=90)
min_holding = 1
cd_price = c.CdTradePrice.CLOSE
slippage = 0
m = 0.9
moneyness_put = -2
nbr_maturity=1
""" Data """
# df_metrics=pd.read_excel('../../../data/df_metrics.xlsx')
# df_index= pd.read_excel('../../../data/df_index.xlsx')
#
# df_metrics = df_metrics[df_metrics[c.Util.DT_DATE]>=start_date].reset_index(drop=True)
# df_index = df_index[df_index[c.Util.DT_DATE]>=start_date].reset_index(drop=True)
# df_metrics[c.Util.DT_DATE] = df_metrics[c.Util.DT_DATE].apply(lambda x: x.date())
# df_index[c.Util.DT_DATE] = df_index[c.Util.DT_DATE].apply(lambda x: x.date())
# df_metrics[c.Util.DT_MATURITY] = df_metrics[c.Util.DT_MATURITY].apply(lambda x: x.date())
df_stocks= pd.read_excel('../../data/十大龙头股组合.xlsx')
df_stocks = df_stocks[(df_stocks['date']>=start_date)&(df_stocks['date']<=end_date)].reset_index(drop=True)
df_stocks[c.Util.DT_DATE] = df_stocks['date'].apply(lambda x: x.date())
df_stocks[c.Util.AMT_CLOSE] = df_stocks['close']
df_stocks[c.Util.ID_INSTRUMENT] = '十大龙头股组合'
df_metrics = get_data.get_50option_mktdata(start_date, end_date)
df_index = get_data.get_index_mktdata(start_date, end_date, c.Util.STR_INDEX_50ETF)
d1 = df_index[c.Util.DT_DATE].values[0]
d2 = df_metrics[c.Util.DT_DATE].values[0]
d = max(d1, d2)
df_metrics = df_metrics[df_metrics[c.Util.DT_DATE] >= d].reset_index(drop=True)
df_index = df_index[df_index[c.Util.DT_DATE] >= d].reset_index(drop=True)
init_index = df_index[c.Util.AMT_CLOSE].values[0]
benchmark = [1]
benchmark1 = [1]
""" Collar """
optionset = BaseOptionSet(df_metrics)
optionset.init()
index = BaseInstrument(df_index)
index.init()
stock = BaseInstrument(df_stocks)
stock.init()
account = BaseAccount(init_fund=c.Util.BILLION, leverage=1.0, rf=0.0)
maturity = optionset.select_maturity_date(nbr_maturity=nbr_maturity, min_holding=min_holding)

# 标的指数开仓
# unit_index =  np.floor(m*account.cash/index.mktprice_close()/index.multiplier())
# init_mktvalue = unit_index*index.mktprice_close()*index.multiplier()
# order_index = account.create_trade_order(index, c.LongShort.LONG, unit_index, cd_trade_price=c.CdTradePrice.CLOSE)
# record_index = index.execute_order(order_index, slippage=slippage)
# account.add_record(record_index, index)
# 标的换成股票指数
init_mktvalue = m*account.cash
unit_stock = np.floor(init_mktvalue/stock.mktprice_close()/stock.multiplier())
order_underlying = account.create_trade_order(stock, c.LongShort.LONG, unit_stock , cd_trade_price=c.CdTradePrice.CLOSE)
record_underlying = stock.execute_order(order_underlying, slippage=slippage)
account.add_record(record_underlying, stock)
init_stock = stock.mktprice_close()
empty_position = True
put = None
while optionset.has_next():
    if maturity > end_date:  # Final close out all.
        close_out_orders = account.creat_close_out_order()
        for order in close_out_orders:
            execution_record = account.dict_holding[order.id_instrument].execute_order(order, slippage=0,
                                                                                       execute_type=c.ExecuteType.EXECUTE_ALL_UNITS)
            account.add_record(execution_record, account.dict_holding[order.id_instrument])

        account.daily_accounting(optionset.eval_date)
        print(optionset.eval_date, ' close out ')
        print(optionset.eval_date, index.eval_date,
              account.account.loc[optionset.eval_date, c.Util.PORTFOLIO_NPV],
              int(account.cash))
        break
    # 平仓:临近到期/行权价平移
    if not empty_position:
        if (maturity - optionset.eval_date).days <= 10:
            empty_position = close_option_position(account)

    # 开仓
    if empty_position:
        maturity = optionset.select_maturity_date(nbr_maturity=nbr_maturity, min_holding=min_holding)
        put = select_target_moneyness_put(c.OptionType.PUT,optionset,moneyness_put,maturity)
        unit_put = np.floor(account.portfolio_total_value/index.mktprice_close()/put.multiplier())
        # unit_put = np.floor(unit_stock*stock.multiplier()*stock.mktprice_close() / put.multiplier())
        order_put = account.create_trade_order(put, c.LongShort.LONG, unit_put, cd_trade_price=cd_price)
        record_put = put.execute_order(order_put, slippage=slippage)
        account.add_record(record_put, put)
        empty_position = False
    account.daily_accounting(optionset.eval_date)
    benchmark.append(index.mktprice_close()/init_index)
    benchmark1.append(stock.mktprice_close()/init_stock)
    if not optionset.has_next(): break
    optionset.next()
    index.next()
    stock.next()

account.account['base_npv'] = benchmark
account.account.to_csv('../account-protective_put1.csv')
account.trade_records.to_csv('../records-protective_put1.csv')
res = account.analysis()
print(res)
dates = list(account.account.index)
npv = list(account.account[c.Util.PORTFOLIO_NPV])
pu.plot_line_chart(dates,[npv,benchmark,benchmark1],['npv','benchmark1','benchmark2'])

plt.show()

