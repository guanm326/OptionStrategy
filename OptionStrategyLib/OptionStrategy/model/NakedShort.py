from back_test.model.base_option_set import BaseOptionSet
from back_test.model.base_account import BaseAccount
from back_test.model.base_option import BaseOption
from back_test.model.base_instrument import BaseInstrument
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
# from WindPy import w


class NakedShort(object):

    def __init__(self,df_metrics,df_baseindex=None,cd_strategy='naked_put',id_baseindex=c.Util.STR_INDEX_300SH,cd_marutity_days=3):
        self.start_date = df_metrics[c.Util.DT_DATE].values[0]
        self.end_date = df_metrics[c.Util.DT_DATE].values[-1]
        if df_baseindex is None:
            df_baseindex = get_data.get_index_mktdata(self.start_date,self.end_date,c.Util.STR_INDEX_300SH)
        self.min_holding = 20
        self.init_fund = c.Util.BILLION
        self.slippage = 0
        self.m = 1  # 期权notional倍数
        if cd_strategy == 'short_straddle':
            self.m = 0.5
        self.moneyness_rank = -4
        self.nbr_maturity = 0
        self.cd_trade_price = c.CdTradePrice.VOLUME_WEIGHTED
        self.account = BaseAccount(init_fund=c.Util.BILLION, leverage=1.0, rf=0.03)
        self.optionset = BaseOptionSet(df_metrics)
        self.optionset.init()
        self.index = BaseInstrument(df_baseindex)
        self.index.init()
        self.cd_strategy = cd_strategy
        self.cd_maturity_days = cd_marutity_days
        self.init_index = self.index.mktprice_close()
        # w.start()
        # TODO: 统一 check dt_first; 将base_npv写入accout


    def close_signal(self):
        dt_maturity = None
        for option in self.account.dict_holding.values():
            if isinstance(option, BaseOption) and option is not None:
                dt_maturity = option.maturitydt()
                break
        # t = w.tdayscount(self.optionset.eval_date.strftime("%Y-%m-%d"), dt_maturity.strftime("%Y-%m-%d"), "").Data[0][0]
        t = c.QuantlibUtil.get_business_between(self.optionset.eval_date,dt_maturity)
        if t <= self.cd_maturity_days:
        # if (dt_maturity - self.optionset.eval_date).days <= self.cd_maturity_days:
            return True
        else:
            return False

    def close_out(self):
        close_out_orders = self.account.creat_close_out_order(cd_trade_price=c.CdTradePrice.CLOSE)
        for order in close_out_orders:
            execution_record = self.account.dict_holding[order.id_instrument] \
                .execute_order(order, slippage=self.slippage, execute_type=c.ExecuteType.EXECUTE_ALL_UNITS)
            self.account.add_record(execution_record, self.account.dict_holding[order.id_instrument])

    def close_all_options(self):
        for option in self.account.dict_holding.values():
            if isinstance(option, BaseOption):
                order = self.account.create_close_order(option, cd_trade_price=self.cd_trade_price)
                record = option.execute_order(order, slippage=self.slippage)
                self.account.add_record(record, option)

    def strategy(self):
        if self.cd_strategy == 'short_straddle':
            return self.short_straddle()
        elif self.cd_strategy == 'short_put':
            return self.short_put()
        elif self.cd_strategy == 'short_call':
            return self.short_call()

    def short_straddle(self):
        maturity1 = self.optionset.select_maturity_date(nbr_maturity=self.nbr_maturity, min_holding=self.min_holding)
        list_atm_call, list_atm_put = self.optionset.get_options_list_by_moneyness_mthd1(
            moneyness_rank=self.moneyness_rank,
            maturity=maturity1, cd_price=c.CdPriceType.OPEN)
        atm_call = self.optionset.select_higher_volume(list_atm_call)
        atm_put = self.optionset.select_higher_volume(list_atm_put)
        if atm_call is None or atm_put is None:
            return
        else:
            return [atm_call,atm_put]

    def short_put(self):
        maturity1 = self.optionset.select_maturity_date(nbr_maturity=self.nbr_maturity, min_holding=self.min_holding)
        list_atm_call, list_atm_put = self.optionset.get_options_list_by_moneyness_mthd1(
            moneyness_rank=self.moneyness_rank,
            maturity=maturity1, cd_price=c.CdPriceType.OPEN)
        atm_put = self.optionset.select_higher_volume(list_atm_put)
        if atm_put is None:
            return
        else:
            return [atm_put]

    def short_call(self):
        maturity1 = self.optionset.select_maturity_date(nbr_maturity=self.nbr_maturity, min_holding=self.min_holding)
        list_atm_call, list_atm_put = self.optionset.get_options_list_by_moneyness_mthd1(
            moneyness_rank=self.moneyness_rank,
            maturity=maturity1, cd_price=c.CdPriceType.OPEN)
        atm_call = self.optionset.select_higher_volume(list_atm_call)
        if atm_call is None:
            return
        else:
            return [atm_call]

    def excute(self,dict_strategy):
        if dict_strategy is None:
            return True
        else:
            pv = self.account.portfolio_total_value
            for option in dict_strategy:
                unit = np.floor(
                    np.floor(pv / option.strike()) / option.multiplier()) * self.m
                order = self.account.create_trade_order(option, c.LongShort.SHORT, unit, cd_trade_price=self.cd_trade_price)
                record = option.execute_order(order, slippage=self.slippage)
                self.account.add_record(record, option)
            return False

    def back_test(self):

        empty_position = True
        index_npv = []
        while self.optionset.eval_date <= self.end_date:

            # print(optionset.eval_date)
            # if self.account.cash <= 0: break
            if self.optionset.eval_date >= self.end_date:  # Final close out all.
                self.close_out()
                self.account.daily_accounting(self.optionset.eval_date)
                index_npv.append(self.index.mktprice_close() / self.init_index)
                break

            # 平仓
            if not empty_position and self.close_signal():
                self.close_all_options()
                empty_position = True

            # 开仓
            if empty_position:
                empty_position = self.excute(self.strategy())

            self.account.daily_accounting(self.optionset.eval_date)
            index_npv.append(self.index.mktprice_close() / self.init_index)
            # print(self.optionset.eval_date,self.account.account.loc[self.optionset.eval_date,c.Util.PORTFOLIO_NPV])
            if not self.optionset.has_next(): break
            self.optionset.next()
            self.index.next()
        self.account.account['index_npv'] = index_npv



""" example """


# df_metrics = get_data.get_50option_mktdata(datetime.date(2015,1,1),datetime.date(2018,11,20))
# df_baseindex = get_data.get_index_mktdata(datetime.date(2015,1,1),datetime.date(2018,11,20),c.Util.STR_INDEX_50SH)
#
# df_sharpe = pd.DataFrame()
# df_return = pd.DataFrame()
# cd_strategy = 'short_straddle'
# for cd_marutity_days in [0,1,2,3,4,5,6,7]:
#     series_sharpe = pd.Series()
#     series_return = pd.Series()
#     for moneyness in [-1,-2,-3,-4]:
#         naked_short = NakedShort(df_metrics,df_baseindex,cd_strategy=cd_strategy,cd_marutity_days=cd_marutity_days)
#         naked_short.moneyness_rank = moneyness
#         naked_short.back_test()
#         sharpe = naked_short.account.analysis()['sharpe']
#         y = naked_short.account.analysis()['annual_yield']
#         series_sharpe['moneyness:'+str(moneyness)] = sharpe
#         series_return['moneyness:'+str(moneyness)] = y
#     df_sharpe[cd_marutity_days] = series_sharpe
#     df_return[cd_marutity_days] = series_return
# df_sharpe.to_csv('../../accounts_data/sharpe_' + str(cd_strategy) +'_2016.csv')
# df_return.to_csv('../../accounts_data/return_' + str(cd_strategy) +'_2016.csv')
#
# df_sharpe = pd.DataFrame()
# df_return = pd.DataFrame()
# cd_strategy = 'short_put'
# for cd_marutity_days in [0,1,2,3,4,5,6,7]:
#     series_sharpe = pd.Series()
#     series_return = pd.Series()
#     for moneyness in [-1,-2,-3,-4]:
#         naked_short = NakedShort(df_metrics,df_baseindex,cd_strategy=cd_strategy,cd_marutity_days=cd_marutity_days)
#         naked_short.moneyness_rank = moneyness
#         naked_short.back_test()
#         sharpe = naked_short.account.analysis()['sharpe']
#         y = naked_short.account.analysis()['annual_yield']
#         series_sharpe['moneyness:'+str(moneyness)] = sharpe
#         series_return['moneyness:'+str(moneyness)] = y
#     df_sharpe[cd_marutity_days] = series_sharpe
#     df_return[cd_marutity_days] = series_return
# df_sharpe.to_csv('../../accounts_data/sharpe_' + str(cd_strategy) +'_2016.csv')
# df_return.to_csv('../../accounts_data/return_' + str(cd_strategy) +'_2016.csv')
#
# df_sharpe = pd.DataFrame()
# df_return = pd.DataFrame()
# cd_strategy = 'short_call'
# for cd_marutity_days in [0,1,2,3,4,5,6,7]:
#     series_sharpe = pd.Series()
#     series_return = pd.Series()
#     for moneyness in [-1,-2,-3,-4]:
#         naked_short = NakedShort(df_metrics,df_baseindex,cd_strategy=cd_strategy,cd_marutity_days=cd_marutity_days)
#         naked_short.moneyness_rank = moneyness
#         naked_short.back_test()
#         sharpe = naked_short.account.analysis()['sharpe']
#         y = naked_short.account.analysis()['annual_yield']
#         series_sharpe['moneyness:'+str(moneyness)] = sharpe
#         series_return['moneyness:'+str(moneyness)] = y
#     df_sharpe[cd_marutity_days] = series_sharpe
#     df_return[cd_marutity_days] = series_return
# df_sharpe.to_csv('../../accounts_data/sharpe_' + str(cd_strategy) +'_2016.csv')
# df_return.to_csv('../../accounts_data/return_' + str(cd_strategy) +'_2016.csv')

# df_metrics = get_data.get_50option_mktdata(datetime.date(2015,1,1),datetime.date(2018,11,20))
# df_baseindex = get_data.get_index_mktdata(datetime.date(2015,1,1),datetime.date(2018,11,20),c.Util.STR_INDEX_50SH)
# df_res = pd.DataFrame()
# cd_strategy = 'short_put'
# for cd_marutity_days in [0,1,2,3,4,5,6,7]:
#
#     naked_short = NakedShort(df_metrics,df_baseindex,cd_strategy=cd_strategy,cd_marutity_days=cd_marutity_days)
#     naked_short.back_test()
#     naked_short.account.account.to_csv('../../accounts_data/naked_short_account_'+ str(cd_strategy) +'_' + str(naked_short.moneyness_rank) + '.csv')
#     naked_short.account.trade_records.to_csv('../../accounts_data/naked_short_records_' + str(cd_strategy) +'_' + str(naked_short.moneyness_rank) + '.csv')
    # res = naked_short.account.analysis()
    # print(res)
    # df_res[cd_marutity_days] = res
# df_res.to_csv('../../accounts_data/res_cd_marutity_days' + str(cd_strategy) +'_'+ str(naked_short.moneyness_rank) + '.csv')

# df_metrics = get_data.get_50option_mktdata(datetime.date(2015,1,1),datetime.date(2018,11,20))
# df_baseindex = get_data.get_index_mktdata(datetime.date(2015,1,1),datetime.date(2018,11,20),c.Util.STR_INDEX_50SH)
#
# df_res = pd.DataFrame()
# for cd_strategy in ['short_call','short_put','short_straddle']:
#     naked_short = NakedShort(df_metrics,df_baseindex,cd_strategy=cd_strategy,cd_marutity_days=5)
#     naked_short.moneyness_rank=-2
#     naked_short.back_test()
#     naked_short.account.account.to_csv('../../accounts_data/naked_short_account_'+ str(cd_strategy) +'_' + str(naked_short.moneyness_rank) + '_2015.csv')
#     naked_short.account.trade_records.to_csv('../../accounts_data/naked_short_records_' + str(cd_strategy) +'_' + str(naked_short.moneyness_rank) + '_2015.csv')
#     res = naked_short.account.analysis()
#     print(res)
#     df_res[cd_strategy] = res
# df_res.to_csv('../../accounts_data/res_cd_strategy_' + str(naked_short.moneyness_rank) + '_2015.csv')

df_metrics = get_data.get_50option_mktdata(datetime.date(2015,2,9),datetime.date(2018,11,20))
df_baseindex = get_data.get_index_mktdata(datetime.date(2015,2,9),datetime.date(2018,11,20),c.Util.STR_INDEX_50SH)

df_res = pd.DataFrame()
for cd_strategy in ['short_call','short_put','short_straddle']:
    naked_short = NakedShort(df_metrics,df_baseindex,cd_strategy=cd_strategy,cd_marutity_days=0)
    naked_short.moneyness_rank=-4
    naked_short.back_test()
    naked_short.account.account.to_csv('../../accounts_data/naked_short_account_'+ str(cd_strategy) +'_' + str(naked_short.moneyness_rank) + '_2015.csv')
    naked_short.account.trade_records.to_csv('../../accounts_data/naked_short_records_' + str(cd_strategy) +'_' + str(naked_short.moneyness_rank) + '_2015.csv')
    res = naked_short.account.analysis()
    print(res)
    df_res[cd_strategy] = res
df_res.to_csv('../../accounts_data/res_cd_strategy_' + str(naked_short.moneyness_rank) + '_2015.csv')


# dates = list(naked_short.account.account.index)
# npv = list(naked_short.account.account[c.Util.PORTFOLIO_NPV])
# pu = PlotUtil()
# pu.plot_line_chart(dates, [npv], ['npv'])
# plt.show()
