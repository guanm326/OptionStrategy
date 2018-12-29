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

# def select_target_moneyness_option(cd_call_put,optionset,moneyness,maturity):
#     list_call_mdt, list_put_mdt = optionset.get_options_list_by_moneyness_mthd1(moneyness_rank=moneyness,
#                                                                                   maturity=maturity)
#     if cd_call_put == c.OptionType.CALL:
#         return optionset.select_higher_volume(list_call_mdt)
#     else:
#         put = optionset.select_higher_volume(list_put_mdt)
#         return put

def select_target_moneyness_option(cd_call_put,optionset,moneyness,maturity):
    list_call_mdt, list_put_mdt = optionset.get_options_list_by_moneyness_mthd1(moneyness_rank=moneyness,
                                                                                  maturity=maturity)
    if cd_call_put == c.OptionType.CALL:
        return optionset.select_higher_volume(list_call_mdt)

    else:
        put = optionset.select_higher_volume(list_put_mdt)
        if put is None: # 选取平值期权
            moneyness += 1
            list_call_mdt, list_put_mdt = optionset.get_options_list_by_moneyness_mthd1(moneyness_rank=moneyness,
                                                                                        maturity=maturity)
            put = optionset.select_higher_volume(list_put_mdt)
            if put is None:
                moneyness += 1
                list_call_mdt, list_put_mdt = optionset.get_options_list_by_moneyness_mthd1(moneyness_rank=moneyness,
                                                                                            maturity=maturity)
                put = optionset.select_higher_volume(list_put_mdt)
            return put
        else:
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
end_date = datetime.date(2018,11,30)
dt_histvol = start_date - datetime.timedelta(days=90)
min_holding = 10
cd_price = c.CdTradePrice.CLOSE
slippage = 0
m = 0.7
moneyness_call = -2
moneyness_put = -2

""" Data """
# df_metrics=pd.read_excel('../../../data/df_metrics.xlsx')
# df_index= pd.read_excel('../../../data/df_index.xlsx')
#
# df_metrics = df_metrics[df_metrics[c.Util.DT_DATE]>=start_date].reset_index(drop=True)
# df_index = df_index[df_index[c.Util.DT_DATE]>=start_date].reset_index(drop=True)
# df_metrics[c.Util.DT_DATE] = df_metrics[c.Util.DT_DATE].apply(lambda x: x.date())
# df_index[c.Util.DT_DATE] = df_index[c.Util.DT_DATE].apply(lambda x: x.date())
# df_metrics[c.Util.DT_MATURITY] = df_metrics[c.Util.DT_MATURITY].apply(lambda x: x.date())
df_metrics = get_data.get_50option_mktdata(start_date, end_date)
df_index = get_data.get_index_mktdata(start_date, end_date, c.Util.STR_INDEX_50ETF)
d1 = df_index[c.Util.DT_DATE].values[0]
d2 = df_metrics[c.Util.DT_DATE].values[0]
d = max(d1, d2)
df_metrics = df_metrics[df_metrics[c.Util.DT_DATE] >= d].reset_index(drop=True)
df_index = df_index[df_index[c.Util.DT_DATE] >= d].reset_index(drop=True)
init_index = df_index[c.Util.AMT_CLOSE].values[0]
benchmark = [1]
""" Collar"""
optionset = BaseOptionSet(df_metrics)
optionset.init()
index = BaseInstrument(df_index)
index.init()
account = BaseAccount(init_fund=c.Util.BILLION, leverage=1.0, rf=0.03)
maturity1 = optionset.select_maturity_date(nbr_maturity=0, min_holding=min_holding)
maturity2 = optionset.select_maturity_date(nbr_maturity=0, min_holding=min_holding)

# 标的指数开仓
unit_index =  np.floor(m*account.cash/index.mktprice_close()/index.multiplier())
option_shares = unit_index
order_index = account.create_trade_order(index, c.LongShort.LONG, unit_index, cd_trade_price=c.CdTradePrice.CLOSE)
record_index = index.execute_order(order_index, slippage=slippage)
account.add_record(record_index, index)
empty_position = True
call = None
put = None
while optionset.has_next():
    if maturity1 > end_date:  # Final close out all.
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
        if (maturity1 - optionset.eval_date).days <= 5:
            empty_position = close_option_position(account)
        elif call is not None:
            spot = call.underlying_close()
            if call.strike() - spot <= 0.05 or put.strike() > spot:
                empty_position = close_option_position(account)

    # 开仓
    if empty_position:
        maturity1 = optionset.select_maturity_date(nbr_maturity=0, min_holding=min_holding)
        maturity2 = optionset.select_maturity_date(nbr_maturity=0, min_holding=min_holding)
        call = select_target_moneyness_option(c.OptionType.CALL,optionset,moneyness_call,maturity1)
        put = select_target_moneyness_option(c.OptionType.PUT,optionset,moneyness_put,maturity2)
        if call is not None:
            unit_call = np.floor(option_shares / call.multiplier())
            order_call = account.create_trade_order(call, c.LongShort.SHORT, unit_call, cd_trade_price=cd_price)
            record_call = call.execute_order(order_call, slippage=slippage)
            account.add_record(record_call, call)
        unit_put = np.floor(option_shares / put.multiplier())
        order_put = account.create_trade_order(put, c.LongShort.LONG, unit_put, cd_trade_price=cd_price)
        record_put = put.execute_order(order_put, slippage=slippage)
        account.add_record(record_put, put)
        empty_position = False
    account.daily_accounting(optionset.eval_date)
    benchmark.append(index.mktprice_close()/init_index)
    if not optionset.has_next(): break
    optionset.next()
    index.next()

account.account['base_npv'] = benchmark
account.account.to_csv('../../accounts_data/collar_account_sh50.csv')
account.trade_records.to_csv('../../accounts_data/collar_records_sh50.csv')
res = account.analysis()
print(res)
dates = list(account.account.index)
npv = list(account.account[c.Util.PORTFOLIO_NPV])
pu.plot_line_chart(dates,[npv,benchmark],['npv','benchmark'])

plt.show()
