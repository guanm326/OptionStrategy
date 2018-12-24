from back_test.model.base_instrument import BaseInstrument
from back_test.model.base_future_coutinuous import BaseFutureCoutinuous
import back_test.model.constant as c
from back_test.model.base_account import BaseAccount
from PricingLibrary.BlackCalculator import BlackCalculator
from PricingLibrary.Options import EuropeanOption
from OptionStrategyLib.VolatilityModel.historical_volatility import HistoricalVolatilityModels as histvol
from Utilities.PlotUtil import PlotUtil
import matplotlib.pyplot as plt
import datetime
import pandas as pd
import numpy as np
import math


# class SytheticOption1(object):
#     def __init__(self, df_index=None, df_future_c1=None, df_future_all=None):
#         if df_index is not None:
#             self.df_base = df_index
#             self.base = BaseInstrument(df_index)
#         else:
#             self.df_base = df_future_c1
#             self.base = BaseFutureCoutinuous(df_future_c1=df_future_c1, df_futures_all_daily=df_future_all)
#         self.base.init()
#         self.account = BaseAccount(c.Util.BILLION * 10)
#         self._prepare_data()
#         self.leverage = 0.75  # Will be multiplied to delta equivalent position
#         self.rf = 0.03
#         self.slippage_date = 1 / 1000.0
#         self.hedge_multiplier = 1
#         self.hold_unit = 0
#         self.target_option = None
#         self.delta_criterian = 0.2
#         self.delta_last_rebalanced = 0.0
#         self.d = 370
#         self.k = 1.1
#
#     def _prepare_data(self):
#         days_1y = 252
#         days_6m = int(days_1y / 2)
#         days_3m = int(days_1y / 4)
#         # 前收盘历史已实现波动率
#         self.df_hv = self.df_base[[c.Util.DT_DATE]]
#         self.df_hv['hv_1y'] = histvol.hist_vol(self.df_base[c.Util.AMT_CLOSE], n=days_1y).shift()
#         self.df_hv['hv_6m'] = histvol.hist_vol(self.df_base[c.Util.AMT_CLOSE], n=days_6m).shift()
#         self.df_hv['hv_3m'] = histvol.hist_vol(self.df_base[c.Util.AMT_CLOSE], n=days_3m).shift()
#         self.df_hv = self.df_hv.dropna().set_index(c.Util.DT_DATE)
#
#     def update_target_option(self):
#         dt_maturity = self.base.eval_date + datetime.timedelta(days=self.d)
#         # self.strike = self.base.mktprice_hist_average(20)*1.05
#         self.strike = self.base.mktprice_close() * self.k
#         self.target_option = EuropeanOption(self.strike, dt_maturity, c.OptionType.CALL)
#         # self.unit_option = np.floor(self.account.portfolio_total_value*self.leverage/self.strike)
#
#     def update_maturity(self):
#         dt_maturity = self.base.eval_date + datetime.timedelta(days=self.d)
#         self.target_option = EuropeanOption(self.strike, dt_maturity, c.OptionType.CALL)
#
#     def get_black_delta(self, vol: float = 0.2):
#         spot = self.base.mktprice_close()
#         date = self.base.eval_date
#         if date in self.df_hv.index:
#             vol = self.df_hv.loc[date, 'hv_6m']
#         # print(vol)
#         black = BlackCalculator(date, self.target_option.dt_maturity, self.target_option.strike,
#                                 self.target_option.option_type, spot, vol, self.rf)
#         delta = round(black.Delta(), 2)
#         return delta
#
#     # Equivalent Delta for Synthetic Option
#     def get_synthetic_delta(self, buywrite) -> float:
#         return buywrite.value * self.get_black_delta()
#
#     def rebalance_sythetic_long(self, delta) -> float:
#         if self.delta_bound_breaked(delta):
#             d_delta = delta - self.delta_last_rebalanced
#             self.delta_last_rebalanced = delta
#             return d_delta
#         else:
#             return 0.0
#
#     # May Add Delta Bound Models Here
#     def delta_bound_breaked(self, delta):
#         if delta - self.delta_last_rebalanced > self.delta_criterian:  # 加仓情况信号下有仓位限制
#             return True
#             # if len(self.account.account)>0 and self.account.account[c.Util.CASH][-1]/self.account.account[c.Util.PORTFOLIO_VALUE][-1]<0.1:
#             #     return False
#             # else:
#             #     return True
#         elif delta - self.delta_last_rebalanced < - self.delta_criterian:
#             return True
#         else:
#             return False
#
#     def close_out(self):
#         close_out_orders = self.account.creat_close_out_order(cd_trade_price=c.CdTradePrice.CLOSE)
#         for order in close_out_orders:
#             execution_record = self.account.dict_holding[order.id_instrument] \
#                 .execute_order(order, slippage_rate=self.slippage_date, execute_type=c.ExecuteType.EXECUTE_ALL_UNITS)
#             self.account.add_record(execution_record, self.account.dict_holding[order.id_instrument])
#
#     def excute(self, sythetic_delta):
#         if sythetic_delta == 0.0: return
#         unit = np.floor(self.account.portfolio_total_value * sythetic_delta / self.base.mktprice_close())
#         # unit = np.floor(self.unit_option * sythetic_delta * self.hedge_multiplier / self.base.multiplier())
#         if unit > 0:
#             long_short = c.LongShort.LONG
#             max_unit = np.floor(self.account.cash * 0.99 / self.base.mktprice_close())
#             unit = min(abs(unit), max_unit)
#         else:
#             long_short = c.LongShort.SHORT
#             hold_unit = self.account.trade_book.loc[id_instrument, c.Util.TRADE_UNIT]
#             unit = min(abs(unit), hold_unit)
#         order = self.account.create_trade_order(self.base, long_short, unit)
#         record = self.base.execute_order(order, slippage_rate=self.slippage_date)
#         self.account.add_record(record, self.base)
#
#     def back_test(self):
#         eval_year = self.base.eval_date.year
#         self.update_target_option()  # Set Init Call Option with strike equals close price
#         init_close = self.base.mktprice_close()
#         # stop_loss = False
#         while self.base.has_next():
#             delta = self.get_synthetic_delta(c.BuyWrite.BUY)
#             self.excute(self.rebalance_sythetic_long(delta))
#             # if not stop_loss:
#             #     if delta < 0.2:
#             #         self.close_out()
#             #         self.delta_last_rebalanced = 0.0
#             #         stop_loss = True
#             #     else:
#             #         self.excute(self.rebalance_sythetic_long(delta))
#             # else:
#             #     if delta >=0.4:
#             #         self.excute(self.rebalance_sythetic_long(delta))
#             #         stop_loss = False
#             self.account.daily_accounting(self.base.eval_date)
#             self.account.account.loc[self.base.eval_date, 'benchmark'] = self.base.mktprice_close() / init_close
#             self.account.account.loc[self.base.eval_date, 'delta'] = self.delta_last_rebalanced
#             # print(self.base.eval_date,self.account.account.loc[self.base.eval_date,c.Util.PORTFOLIO_NPV])
#             self.base.next()
#
#             if self.base.eval_date.year != eval_year:
#                 eval_year = self.base.eval_date.year
#                 self.update_target_option()  # Update option at last trading day of the year
#                 # stop_loss = False
#             self.update_maturity()
#             # if self.base.is_end_of_quater():
#             #     self.update_target_option()
#
#         return self.account


class SytheticOption(object):
    def __init__(self, df_index=None, df_future_c1=None, df_future_all=None):
        if df_index is not None:
            self.df_base = df_index
            self.base = BaseInstrument(df_index)
        else:
            self.df_base = df_future_c1
            self.base = BaseFutureCoutinuous(df_future_c1=df_future_c1, df_futures_all_daily=df_future_all)
        self.base.init()
        self.account = BaseAccount(c.Util.BILLION * 10)
        self._prepare_data()
        self.leverage = 0.75  # Will be multiplied to delta equivalent position
        self.rf = 0.03
        self.slippage_date = 1 / 1000.0
        self.hedge_multiplier = 1
        self.hold_unit = 0
        self.target_option = None
        self.cd_delta_bound = 'ww'
        self.delta_criterian = 0.1
        self.delta_last_rebalanced = 0.0
        self.d = 50
        self.k = 1.1
        self.H = None

    def _prepare_data(self):
        days_1y = 252
        days_6m = int(days_1y / 2)
        days_3m = int(days_1y / 4)
        # 前收盘历史已实现波动率
        self.df_hv = self.df_base[[c.Util.DT_DATE]]
        self.df_hv['hv_1y'] = histvol.hist_vol(self.df_base[c.Util.AMT_CLOSE], n=days_1y).shift()
        self.df_hv['hv_6m'] = histvol.hist_vol(self.df_base[c.Util.AMT_CLOSE], n=days_6m).shift()
        self.df_hv['hv_3m'] = histvol.hist_vol(self.df_base[c.Util.AMT_CLOSE], n=days_3m).shift()
        self.df_hv = self.df_hv.dropna().set_index(c.Util.DT_DATE)

    def update_target_option(self):
        self.dt_maturity = self.base.eval_date + datetime.timedelta(days=self.d)
        # self.strike = self.base.mktprice_hist_average(20)*1.05
        self.strike = self.base.mktprice_close() * self.k
        self.target_option = EuropeanOption(self.strike, self.dt_maturity, c.OptionType.CALL)
        # self.unit_option = np.floor(self.account.portfolio_total_value*self.leverage/self.strike)

    def update_maturity(self):
        self.dt_maturity = self.base.eval_date + datetime.timedelta(days=self.d)
        self.target_option = EuropeanOption(self.strike, self.dt_maturity, c.OptionType.CALL)

    def get_black_delta(self, vol: float = 0.2):
        spot = self.base.mktprice_close()
        date = self.base.eval_date
        if date in self.df_hv.index:
            vol = self.df_hv.loc[date, 'hv_6m']
        # print(vol)
        black = BlackCalculator(date, self.target_option.dt_maturity, self.target_option.strike,
                                self.target_option.option_type, spot, vol, self.rf)
        delta = round(black.Delta(), 2)
        return delta

    def get_black_gamma(self, vol: float = 0.2):
        spot = self.base.mktprice_close()
        date = self.base.eval_date
        if date in self.df_hv.index:
            vol = self.df_hv.loc[date, 'hv_6m']
        # print(vol)
        black = BlackCalculator(date, self.target_option.dt_maturity, self.target_option.strike,
                                self.target_option.option_type, spot, vol, self.rf)
        gamma = black.Gamma()
        return gamma

    # Equivalent Delta for Synthetic Option
    def get_synthetic_delta(self, buywrite) -> float:
        return buywrite.value * self.get_black_delta()

    def rebalance_sythetic_long(self, delta) -> float:
        if self.delta_bound_breaked(delta) or self.delta_last_rebalanced==0.0:
            # d_delta = delta - self.delta_last_rebalanced
            self.delta_last_rebalanced = delta
            # return d_delta
            return delta
        else:
            return 0.0

    # May Add Delta Bound Models Here
    def delta_bound_breaked(self, delta):
        if self.cd_delta_bound == 'ww':
            gamma = self.get_black_gamma()
            self.H = self.whalley_wilmott(self.base.eval_date, self.base.mktprice_close(), gamma, self.dt_maturity)
            if abs(delta - self.delta_last_rebalanced) > self.H:
                return True
            else:
                return False
        else:
            if abs(delta - self.delta_last_rebalanced) > self.delta_criterian:
                return True
            else:
                return False

    def whalley_wilmott(self, eval_date, spot, gamma,dt_maturity, rho=0.01):
        fee = self.slippage_date
        ttm = c.PricingUtil.get_ttm(eval_date, dt_maturity)
        H = (1.5 * math.exp(-self.rf * ttm) * fee * spot * (gamma ** 2) / rho) ** (1 / 3)
        return H

    def close_out(self):
        close_out_orders = self.account.creat_close_out_order(cd_trade_price=c.CdTradePrice.CLOSE)
        for order in close_out_orders:
            execution_record = self.account.dict_holding[order.id_instrument] \
                .execute_order(order, slippage_rate=self.slippage_date, execute_type=c.ExecuteType.EXECUTE_ALL_UNITS)
            self.account.add_record(execution_record, self.account.dict_holding[order.id_instrument])

    def excute(self, sythetic_delta):
        if sythetic_delta == 0.0: return
        # sythetic_unit = np.floor(self.account.portfolio_total_value * sythetic_delta / self.base.mktprice_close())
        sythetic_unit = np.floor((self.hold_unit*self.base.mktprice_close()+self.account.cash) * sythetic_delta / self.base.mktprice_close())
        unit = sythetic_unit - self.hold_unit
        if unit > 0:
            long_short = c.LongShort.LONG
            max_unit = np.floor(self.account.cash * 0.99 / self.base.mktprice_close())
            unit = min(abs(unit), max_unit)
            self.hold_unit += unit
        else:
            long_short = c.LongShort.SHORT
            hold_unit = self.account.trade_book.loc[self.base.id_instrument(), c.Util.TRADE_UNIT]
            unit = min(abs(unit), hold_unit)
            self.hold_unit -= unit
        order = self.account.create_trade_order(self.base, long_short, unit)
        record = self.base.execute_order(order, slippage_rate=self.slippage_date)
        self.account.add_record(record, self.base)

    def back_test(self):
        eval_year = self.base.eval_date.year
        self.update_target_option()  # Set Init Call Option with strike equals close price
        init_close = self.base.mktprice_close()
        self.account.daily_accounting(self.base.eval_date)
        self.account.account.loc[self.base.eval_date, 'benchmark'] = self.base.mktprice_close() / init_close
        self.account.account.loc[self.base.eval_date, 'delta'] = self.delta_last_rebalanced
        self.account.account.loc[self.base.eval_date, 'ww_bound'] = self.H
        self.base.next()
        while self.base.has_next():
            delta = self.get_synthetic_delta(c.BuyWrite.BUY)
            self.excute(self.rebalance_sythetic_long(delta))
            self.account.daily_accounting(self.base.eval_date)
            self.account.account.loc[self.base.eval_date, 'benchmark'] = self.base.mktprice_close() / init_close
            self.account.account.loc[self.base.eval_date, 'delta'] = self.delta_last_rebalanced
            self.account.account.loc[self.base.eval_date, 'ww_bound'] = self.H
            if self.base.next_date().year != eval_year:
                eval_year = self.base.next_date().year
                self.update_target_option()  # Update option at last trading day of the year
            self.base.next()
            self.update_maturity()
        self.account.daily_accounting(self.base.eval_date)
        self.account.account.loc[self.base.eval_date, 'benchmark'] = self.base.mktprice_close() / init_close
        self.account.account.loc[self.base.eval_date, 'delta'] = self.delta_last_rebalanced
        self.account.account.loc[self.base.eval_date, 'ww_bound'] = self.H
        return self.account



################# Good Year Historical Simulation: 2007 ########################
df_simulation_npvs = pd.DataFrame()
df_simulation_analysis = pd.DataFrame()
# df_simulation_mdd = pd.DataFrame()
df_simulation = pd.read_excel('../../../data/df_simulation1000.xlsx')
dates = df_simulation[c.Util.DT_DATE].apply(lambda x: x.date())
df_simulation_npvs[c.Util.DT_DATE] = dates
df_simulation_npvs = df_simulation_npvs.set_index(c.Util.DT_DATE,drop=True)
for col in df_simulation.columns.values:
    if col == c.Util.DT_DATE: continue
    print(col)
    df_base = pd.DataFrame()
    df_base[c.Util.AMT_CLOSE] = df_simulation[col]
    df_base[c.Util.DT_DATE] = dates
    df_base[c.Util.ID_INSTRUMENT] = '000985.CSI'
    sythetic = SytheticOption(df_index=df_base)
    sythetic.d = 50
    sythetic.cd_delta_bound = 'ww'
    account = sythetic.back_test()
    npvs = account.account[c.Util.PORTFOLIO_NPV]
    df_simulation_npvs['npv_'+col] = account.account[c.Util.PORTFOLIO_NPV]
    df_yearly =account.annual_analyis()[0].loc['2007']
    df_yearly['SimNo'] = col
    df_simulation_analysis = df_simulation_analysis.append(df_yearly,ignore_index=True)
df_simulation_npvs.to_csv('../../accounts_data/df_simulation_npvs_1000_2007.csv')
df_simulation_analysis.to_csv('../../accounts_data/df_simulation_analysis_1000_2007.csv')

################# Bad Year Historical Simulation: 2008 ########################
df_simulation_npvs = pd.DataFrame()
df_simulation_analysis = pd.DataFrame()
# df_simulation_mdd = pd.DataFrame()
df_simulation = pd.read_excel('../../../data/df_simulation1000_1.xlsx')
dates = df_simulation[c.Util.DT_DATE].apply(lambda x: x.date())
df_simulation_npvs[c.Util.DT_DATE] = dates
df_simulation_npvs = df_simulation_npvs.set_index(c.Util.DT_DATE,drop=True)
for col in df_simulation.columns.values:
    if col == c.Util.DT_DATE: continue
    print(col)
    df_base = pd.DataFrame()
    df_base[c.Util.AMT_CLOSE] = df_simulation[col]
    df_base[c.Util.DT_DATE] = dates
    df_base[c.Util.ID_INSTRUMENT] = '000985.CSI'
    sythetic = SytheticOption(df_index=df_base)
    sythetic.d = 50
    sythetic.cd_delta_bound = 'ww'
    account = sythetic.back_test()
    npvs = account.account[c.Util.PORTFOLIO_NPV]
    df_simulation_npvs['npv_'+col] = account.account[c.Util.PORTFOLIO_NPV]
    df_yearly =account.annual_analyis()[0].loc['2008']
    df_yearly['SimNo'] = col
    df_simulation_analysis = df_simulation_analysis.append(df_yearly,ignore_index=True)
df_simulation_npvs.to_csv('../../accounts_data/df_simulation_npvs_1000_2008.csv')
df_simulation_analysis.to_csv('../../accounts_data/df_simulation_analysis_1000_2008.csv')


#
# df_base = pd.read_excel('../../../data/中证全指日收盘价.xlsx')
# df_base[c.Util.DT_DATE] = df_base['日期'].apply(lambda x: x.date())
# df_base = df_base.rename(columns={'000985.CSI': c.Util.AMT_CLOSE})
# id_instrument = '000985.CSI'
# df_base[c.Util.ID_INSTRUMENT] = id_instrument

# sythetic = SytheticOption(df_index=df_base)
# sythetic.k = 1.1
# sythetic.d = 50
# account = sythetic.back_test()
# df_res_k[str(k)] = account.analysis()
# account.account.to_csv('../../accounts_data/sythetic_account.csv')
# account.trade_records.to_csv('../../accounts_data/sythetic_records.csv')
# res = account.analysis()
# print(res)
# df_yearly,df_yearly_npvs = account.annual_analyis()
# print(df_yearly)
# df_yearly.to_csv('../../accounts_data/df_yearly.csv')
# df_yearly_npvs.to_csv('../../accounts_data/df_yearly_npvs.csv')
# pu = PlotUtil()
# dates = list(account.account.index)
# npv = list(account.account[c.Util.PORTFOLIO_NPV])
# benchmark = list(account.account['benchmark'])
# pu.plot_line_chart(dates, [npv,benchmark], ['npv','benchmark'])
# plt.show()

######### Delta Bounds ###################
# npvs = []
# df_yield_d = pd.DataFrame()
# df_mdd_d = pd.DataFrame()
# df_res_d = pd.DataFrame()
# for d_c in ['ww',0.05,0.1,0.2]:
#     print(d_c)
#     sythetic = SytheticOption(df_index=df_base)
#     sythetic.k = 1.0
#     sythetic.d = 50
#     sythetic.cd_delta_bound = d_c
#     sythetic.delta_criterian = d_c
#     account = sythetic.back_test()
#     npvs.append(list(account.account[c.Util.PORTFOLIO_NPV]))
#     df_yearly =account.annual_analyis()[0]
#     df_yield_d[str(d_c)] = df_yearly['accumulate_yield']
#     df_mdd_d[str(d_c)] = df_yearly['max_absolute_loss']
#     df_res_d[str(d_c)] = account.analysis()
#     account.account.to_csv('../../accounts_data/sythetic_account'+str(sythetic.k)+str(sythetic.delta_criterian)+'.csv')
#     account.trade_records.to_csv('../../accounts_data/sythetic_records'+str(sythetic.k)+str(sythetic.delta_criterian)+'.csv')
#
# df_res_d.to_csv('../../accounts_data/df_res_d'+str(sythetic.k)+'.csv')
# df_mdd_d.to_csv('../../accounts_data/df_mdd_d'+str(sythetic.k)+'.csv')
# df_yield_d.to_csv('../../accounts_data/df_yield_d'+str(sythetic.k)+'.csv')
# print(account.analysis())
# pu = PlotUtil()
# dates = list(account.account.index)
# npvs.append(list(account.account['benchmark']))
# pu.plot_line_chart(dates, npvs, ['NPV (delta bound Whalley Wilmott)','NPV (delta bound=0.05)','NPV (delta bound=0.1)','NPV (delta bound=0.2)','benchmark'])
# plt.show()

######### Strikes ###################

# npvs = []
# df_yield_k = pd.DataFrame()
# df_mdd_k = pd.DataFrame()
# df_res_k = pd.DataFrame()
# # for k in [1.0, 1.05, 1.1]:
# for k in [1.1]:
#     sythetic = SytheticOption(df_index=df_base)
#     sythetic.k = k
#     sythetic.d = 50
#     # sythetic.delta_criterian = 0.1
#     account = sythetic.back_test()
#     npvs.append(list(account.account[c.Util.PORTFOLIO_NPV]))
#     df_yearly =account.annual_analyis()[0]
#     df_yield_k[str(k)] = df_yearly['accumulate_yield']
#     df_mdd_k[str(k)] = df_yearly['max_absolute_loss']
#     df_res_k[str(k)] = account.analysis()
#     account.account.to_csv('../../accounts_data/ww_sythetic_account'+str(sythetic.k)+'.csv')
#     account.trade_records.to_csv('../../accounts_data/ww_sythetic_records'+str(sythetic.k)+'.csv')
# df_res_k.to_csv('../../accounts_data/ww_df_res_k.csv')
# df_mdd_k.to_csv('../../accounts_data/ww_df_mdd_k.csv')
# df_yield_k.to_csv('../../accounts_data/ww_df_yield_k.csv')
# print(account.analysis())
# pu = PlotUtil()
# dates = list(account.account.index)
# npvs.append(list(account.account['benchmark']))
# pu.plot_line_chart(dates, npvs, ['NPV (K=100%)','NPV (K=105%)','NPV (K=110%)','benchmark'])
# plt.show()


######### Ts ###################

# df_yield = pd.DataFrame()
# df_mdd = pd.DataFrame()
# npvs = []
# df_npvs = pd.DataFrame()
# df_res = pd.DataFrame()
# for d in [30,40,50,60,70,80,90]:
# # for d in [50]:
#     print(d)
#     sythetic = SytheticOption(df_index=df_base)
#     sythetic.d = d
#     # sythetic.delta_criterian = 0.1
#     sythetic.cd_delta_bound = 'ww'
#     account = sythetic.back_test()
#     npvs.append(list(account.account[c.Util.PORTFOLIO_NPV]))
#     df_npvs['npv '+str(d) + ' day'] = list(account.account[c.Util.PORTFOLIO_NPV])
#     df_res['npv '+str(d) + ' day'] = account.analysis()
#     df_yearly =account.annual_analyis()[0]
#     df_yield['npv '+str(d) + ' day'] = df_yearly['accumulate_yield']
#     df_mdd['npv '+str(d) + ' day'] = df_yearly['max_absolute_loss']
# df_npvs['dt_date'] = list(account.account.index)
# df_npvs['benchmark'] = list(account.account['benchmark'])
# df_npvs.to_csv('../../accounts_data/df_npvs.csv')
# df_res.to_csv('../../accounts_data/df_res.csv')
# df_yield.to_csv('../../accounts_data/df_yield.csv')
# df_mdd.to_csv('../../accounts_data/df_mdd.csv')
# pu = PlotUtil()
# dates = list(account.account.index)
# npvs.append(list(account.account['benchmark']))
# pu.plot_line_chart(dates, npvs, ['NPV (T=30Day)','NPV (T=40Day)','NPV (T=50Day)','NPV (T=60Day)','NPV (T=70Day)','NPV (T=80Day)','NPV (T=90Day)','benchmark'])
# plt.show()
