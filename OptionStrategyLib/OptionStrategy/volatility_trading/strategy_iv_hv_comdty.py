from back_test.model.base_option_set import BaseOptionSet
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
from back_test.model.trade import Order
from OptionStrategyLib.VolatilityModel.historical_volatility import HistoricalVolatilityModels as histvol


def open_position( df_vol, dt_date):
    return True
    # if dt_date not in df_vol.index:
    #     return False
    # amt_premium = df_vol.loc[dt_date, 'amt_premium']
    # amt_1std = df_vol.loc[dt_date, 'amt_1std']
    # if amt_premium > amt_1std and amt_premium >0:
    #     print(dt_date,' open position')
    #     return True
    # else:
    #     return False

def close_position(df_vol, dt_maturity, optionset):

    if (dt_maturity - optionset.eval_date).days <= 5:
        return True
    else:
        return False
    # dt_date = optionset.eval_date
    # amt_premium = df_vol.loc[dt_date, 'amt_premium']
    # amt_n1std = df_vol.loc[dt_date, 'amt_n1std']
    # if amt_premium < amt_n1std or amt_premium <=0:
    #     print(dt_date,' close position')
    #     return True
    # else:
    #     return False


pu = PlotUtil()
start_date = datetime.date(2018, 9, 1)
end_date = datetime.date(2018, 12, 3)
dt_histvol = start_date - datetime.timedelta(days=300)
min_holding = 20  # 20 sharpe ratio较优
slippage = 0
m = 3  # 期权notional倍数
cd_vw_price = c.CdTradePrice.VOLUME_WEIGHTED
cd_c_price = c.CdTradePrice.CLOSE

name_code = c.Util.STR_CU
# name_code = c.Util.STR_M
df_metrics = get_data.get_comoption_mktdata(start_date, end_date,name_code)
df_future_c1_daily = get_data.get_future_c1_by_option_daily(dt_histvol, end_date, name_code,min_holding=5)
df_futures_all_daily = get_data.get_mktdata_future_daily(start_date, end_date,
                                                         name_code)  # daily data of all future contracts


df_future_c1_daily['amt_hv'] = histvol.hist_vol(df_future_c1_daily[c.Util.AMT_CLOSE],n=30)

df_iv = get_data.get_iv_by_moneyness(dt_histvol, end_date, name_code)
# df_iv_call = df_iv[df_iv[c.Util.CD_OPTION_TYPE] == 'call']
# df_iv_put = df_iv[df_iv[c.Util.CD_OPTION_TYPE] == 'put']
df_iv_htbr = df_iv[df_iv[c.Util.CD_OPTION_TYPE]=='put_call_htbr']
# df_data = df_iv_call[[c.Util.DT_DATE, c.Util.PCT_IMPLIED_VOL]].rename(columns={c.Util.PCT_IMPLIED_VOL: 'iv_call'})
# df_data = df_data.join(df_iv_put[[c.Util.DT_DATE, c.Util.PCT_IMPLIED_VOL]].set_index(c.Util.DT_DATE), on=c.Util.DT_DATE,
#                        how='outer') \
#     .rename(columns={c.Util.PCT_IMPLIED_VOL: 'iv_put'})
# df_data = df_data.dropna().reset_index(drop=True)
df_data = df_iv_htbr.reset_index(drop=True).rename(columns={c.Util.PCT_IMPLIED_VOL:'amt_iv'})
# df_data.loc[:, 'amt_iv'] = (df_data.loc[:, 'iv_call'] + df_data.loc[:, 'iv_put']) / 2
df_vol = pd.merge(df_data[[c.Util.DT_DATE, 'amt_iv']], df_future_c1_daily[[c.Util.DT_DATE, 'amt_hv']],
                  on=c.Util.DT_DATE)
df_vol['amt_premium'] = (df_vol['amt_iv'] - df_vol['amt_hv']).shift()
df_vol['amt_iv_previous'] = df_vol['amt_iv'].shift()
df_vol = df_vol.dropna().reset_index(drop=True)
h = 10
df_vol['amt_1std'] = c.Statistics.moving_average(df_vol['amt_premium'], n=h)+c.Statistics.standard_deviation(df_vol['amt_premium'], n=h)
df_vol['amt_n1std'] = c.Statistics.moving_average(df_vol['amt_premium'], n=h)-c.Statistics.standard_deviation(df_vol['amt_premium'], n=h)
df_vol['amt_2std'] = c.Statistics.moving_average(df_vol['amt_premium'], n=h)+2*c.Statistics.standard_deviation(df_vol['amt_premium'], n=h)
df_vol['amt_n2std'] = c.Statistics.moving_average(df_vol['amt_premium'], n=h)-2*c.Statistics.standard_deviation(df_vol['amt_premium'], n=h)
df_vol = df_vol.set_index(c.Util.DT_DATE)
df_vol['iv_percentile'] = c.Statistics.standard_deviation(df_vol['amt_iv'],n=252)
df_vol.to_csv('../../accounts_data/implied_vol_premium.csv')
print('premium mean : ',df_vol['amt_premium'].sum()/len(df_vol['amt_premium']))
dates = list(df_vol.index)
pu.plot_line_chart(dates, [list(df_vol['amt_premium']), list(df_vol['amt_1std']),list(df_vol['amt_n1std'])],
                   ['隐含与历史波动率价差','基于'+str(h)+'日移动平均的1倍标准差','基于'+str(h)+'日移动平均的n1倍标准差'])

# plt.show()

df_holding_period = pd.DataFrame()

d = max(df_future_c1_daily[c.Util.DT_DATE].values[0], df_metrics[c.Util.DT_DATE].values[0])
df_metrics = df_metrics[df_metrics[c.Util.DT_DATE] >= d].reset_index(drop=True)
df_c1 = df_future_c1_daily[df_future_c1_daily[c.Util.DT_DATE] >= d].reset_index(drop=True)
df_c_all = df_futures_all_daily[df_futures_all_daily[c.Util.DT_DATE] >= d].reset_index(drop=True)


optionset = BaseOptionSet(df_metrics)
optionset.init()
d1 = optionset.eval_date

hedging = SytheticOption(df_c1, frequency=c.FrequentType.DAILY, df_c1_daily=df_c1,df_futures_all_daily = df_c_all)
hedging.init()
# hedging.amt_option = 1 / 1000  # 50ETF与IH点数之比

account = BaseAccount(init_fund=c.Util.MILLION*10, leverage=1.0, rf=0.03)

option_trade_times = 0
empty_position = True
unit_p = None
unit_c = None
atm_strike = None
buy_write = c.BuyWrite.WRITE
maturity1 = optionset.select_maturity_date(nbr_maturity=0, min_holding=min_holding)
id_future = hedging.current_state[c.Util.ID_FUTURE]
idx_hedge = 0
flag_hedge = False
while optionset.eval_date <= end_date:
    # if account.cash <= 0: break
    if optionset.eval_date >= end_date:  # Final close out all.
        close_out_orders = account.creat_close_out_order()
        for order in close_out_orders:
            execution_record = account.dict_holding[order.id_instrument].execute_order(order, slippage=0,
                                                                                       execute_type=c.ExecuteType.EXECUTE_ALL_UNITS)
            account.add_record(execution_record, account.dict_holding[order.id_instrument])

        account.daily_accounting(optionset.eval_date)
        print(optionset.eval_date, ' close out ')
        print(optionset.eval_date, hedging.eval_date,
              account.account.loc[optionset.eval_date, c.Util.PORTFOLIO_NPV],
              int(account.cash))
        break

    # 标的移仓换月
    if id_future != hedging.current_state[c.Util.ID_FUTURE]:
        for holding in account.dict_holding.values():
            if isinstance(holding, SytheticOption):
                df = hedging.df_all_futures_daily[
                    (hedging.df_all_futures_daily[c.Util.DT_DATE] == hedging.eval_date) & (
                        hedging.df_all_futures_daily[c.Util.ID_FUTURE] == id_future)]
                trade_unit = account.trade_book.loc[hedging.name_code(), c.Util.TRADE_UNIT]
                if account.trade_book.loc[hedging.name_code(), c.Util.TRADE_LONG_SHORT] == c.LongShort.LONG:
                    long_short = c.LongShort.SHORT
                else:
                    long_short = c.LongShort.LONG
                trade_price = df[c.Util.AMT_CLOSE].values[0]
                order = Order(holding.eval_date, hedging.name_code(), trade_unit, trade_price,
                              holding.eval_datetime, long_short)
                record = hedging.execute_order(order, slippage=slippage)
                account.add_record(record, holding)
        hedging.synthetic_unit = 0
        id_future = hedging.current_state[c.Util.ID_FUTURE]
        flag_hedge = True

    # 平仓：距到期8日
    if not empty_position:
        if close_position(df_vol, maturity1, optionset):
            for option in account.dict_holding.values():
                if isinstance(option,BaseOption):
                    order = account.create_close_order(option, cd_trade_price=cd_vw_price)
                else:
                    order = account.create_close_order(option, cd_trade_price=cd_c_price)
                record = option.execute_order(order, slippage=slippage)
                account.add_record(record, option)
                hedging.synthetic_unit = 0
            empty_position = True

    # 开仓：距到期1M
    if empty_position and open_position(df_vol, optionset.eval_date):
        maturity1 = optionset.select_maturity_date(nbr_maturity=0, min_holding=min_holding)
        option_trade_times += 1
        buy_write = c.BuyWrite.WRITE
        long_short = c.LongShort.SHORT
        list_atm_call, list_atm_put = optionset.get_options_list_by_moneyness_mthd1(moneyness_rank=0,
                                                                          maturity=maturity1,
                                                                          cd_price=c.CdPriceType.OPEN)
        # list_atm_call, xx = optionset.get_options_list_by_moneyness_mthd1(moneyness_rank=-1,
        #                                                                             maturity=maturity1,
        #                                                                             cd_price=c.CdPriceType.OPEN)
        # xxx, list_atm_put = optionset.get_options_list_by_moneyness_mthd1(moneyness_rank=1,
        #                                                                             maturity=maturity1,
        #                                                                             cd_price=c.CdPriceType.OPEN)
        atm_call = optionset.select_higher_volume(list_atm_call)
        atm_put = optionset.select_higher_volume(list_atm_put)
        atm_strike = atm_call.strike()
        spot = atm_call.underlying_close()
        unit_c = np.floor(np.floor(account.portfolio_total_value / atm_call.strike()) / atm_call.multiplier()) * m
        unit_p = np.floor(np.floor(account.portfolio_total_value / atm_put.strike()) / atm_put.multiplier()) * m
        order_c = account.create_trade_order(atm_call, long_short, unit_c, cd_trade_price=cd_vw_price)
        order_p = account.create_trade_order(atm_put, long_short, unit_p, cd_trade_price=cd_vw_price)
        record_call = atm_call.execute_order(order_c, slippage=slippage)
        record_put = atm_put.execute_order(order_p, slippage=slippage)
        account.add_record(record_call, atm_call)
        account.add_record(record_put, atm_put)
        empty_position = False

    # Delta hedge
    if not empty_position:
        iv_htbr = optionset.get_iv_by_otm_iv_curve(dt_maturity=maturity1, strike=atm_call.applicable_strike())
        delta_call = atm_call.get_delta(iv_htbr)
        delta_put = atm_put.get_delta(iv_htbr)
        options_delta = unit_c * atm_call.multiplier() * delta_call + unit_p * atm_put.multiplier() * delta_put
        hedge_unit = hedging.get_hedge_rebalancing_unit(options_delta, buy_write)
        hedging.synthetic_unit += - hedge_unit
        if hedge_unit > 0:
            long_short = c.LongShort.LONG
        else:
            long_short = c.LongShort.SHORT
        order_u = account.create_trade_order(hedging, long_short, hedge_unit, cd_trade_price=cd_c_price)
        record_u = hedging.execute_order(order_u, slippage=slippage)
        account.add_record(record_u, hedging)
        flag_hedge = False

    idx_hedge += 1
    # if optionset.eval_date == datetime.date(2018,12,3):
    #     print('')
    account.daily_accounting(optionset.eval_date)
    total_liquid_asset = account.cash + account.get_portfolio_margin_capital()
    if not optionset.has_next(): break
    optionset.next()
    hedging.next()

account.account.to_csv('../../accounts_data/iv_hv_account_comdty.csv')
account.trade_records.to_csv('../../accounts_data/iv_hv_record_comdty.csv')
res = account.analysis()
# res['期权平均持仓天数'] = len(account.account) / option_trade_times
print(res)
# print(account.trade_records)
dates = list(account.account.index)
npv = list(account.account[c.Util.PORTFOLIO_NPV])
pu.plot_line_chart(dates, [npv], ['npv'])

plt.show()
