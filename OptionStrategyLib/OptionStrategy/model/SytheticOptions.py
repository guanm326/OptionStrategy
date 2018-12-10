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
        self.slippage_date = 1/1000.0
        self.hedge_multiplier = 1
        self.hold_unit = 0
        self.target_option = None
        self.delta_criterian = 0.2
        self.delta_last_rebalanced = 0.0
        self.d = 370

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
        dt_maturity = self.base.eval_date + datetime.timedelta(days=self.d)
        # self.strike = self.base.mktprice_hist_average(20)*1.05
        self.strike = self.base.mktprice_close()*1.05
        self.target_option = EuropeanOption(self.strike, dt_maturity, c.OptionType.CALL)
        # self.unit_option = np.floor(self.account.portfolio_total_value*self.leverage/self.strike)

    def update_maturity(self):
        dt_maturity = self.base.eval_date + datetime.timedelta(days=self.d)
        self.target_option = EuropeanOption(self.strike, dt_maturity, c.OptionType.CALL)

    def get_black_delta(self, vol: float = 0.2):
        spot = self.base.mktprice_close()
        date = self.base.eval_date
        if date in self.df_hv.index:
            vol = self.df_hv.loc[date, 'hv_6m']
        # print(vol)
        black = BlackCalculator(date, self.target_option.dt_maturity, self.target_option.strike,
                                self.target_option.option_type, spot, vol, self.rf)
        delta = round(black.Delta(),2)
        return delta

    # Equivalent Delta for Synthetic Option
    def get_synthetic_delta(self, buywrite) -> float:
        return buywrite.value * self.get_black_delta()

    def rebalance_sythetic_long(self,delta) -> float:
        if self.delta_bound_breaked(delta):
            d_delta = delta - self.delta_last_rebalanced
            self.delta_last_rebalanced = delta
            return d_delta
        else:
            return 0.0

    # May Add Delta Bound Models Here
    def delta_bound_breaked(self, delta):
        if delta - self.delta_last_rebalanced > self.delta_criterian: # 加仓情况信号下有仓位限制
            return True
            # if len(self.account.account)>0 and self.account.account[c.Util.CASH][-1]/self.account.account[c.Util.PORTFOLIO_VALUE][-1]<0.1:
            #     return False
            # else:
            #     return True
        elif delta - self.delta_last_rebalanced <- self.delta_criterian:
            return True
        else:
            return False

    def close_out(self):
        close_out_orders = self.account.creat_close_out_order(cd_trade_price=c.CdTradePrice.CLOSE)
        for order in close_out_orders:
            execution_record = self.account.dict_holding[order.id_instrument] \
                .execute_order(order, slippage_rate=self.slippage_date, execute_type=c.ExecuteType.EXECUTE_ALL_UNITS)
            self.account.add_record(execution_record, self.account.dict_holding[order.id_instrument])

    def excute(self,sythetic_delta):
        if sythetic_delta ==0.0 : return
        unit = np.floor(self.account.portfolio_total_value*sythetic_delta/self.base.mktprice_close())
        # unit = np.floor(self.unit_option * sythetic_delta * self.hedge_multiplier / self.base.multiplier())
        if unit >0:
            long_short = c.LongShort.LONG
            max_unit = np.floor(self.account.cash/self.base.mktprice_close())
            unit = min(abs(unit),max_unit)
        else:
            long_short = c.LongShort.SHORT
            hold_unit = self.account.trade_book.loc[id_instrument,c.Util.TRADE_UNIT]
            unit = min(abs(unit),hold_unit)
        order = self.account.create_trade_order(self.base, long_short, unit)
        record = self.base.execute_order(order, slippage_rate=self.slippage_date)
        self.account.add_record(record, self.base)

    def back_test(self):
        eval_year = self.base.eval_date.year
        self.update_target_option() # Set Init Call Option with strike equals close price
        init_close = self.base.mktprice_close()
        # stop_loss = False
        while self.base.has_next():
            delta = self.get_synthetic_delta(c.BuyWrite.BUY)
            self.excute(self.rebalance_sythetic_long(delta))
            # if not stop_loss:
            #     if delta < 0.2:
            #         self.close_out()
            #         self.delta_last_rebalanced = 0.0
            #         stop_loss = True
            #     else:
            #         self.excute(self.rebalance_sythetic_long(delta))
            # else:
            #     if delta >=0.4:
            #         self.excute(self.rebalance_sythetic_long(delta))
            #         stop_loss = False
            self.account.daily_accounting(self.base.eval_date)
            self.account.account.loc[self.base.eval_date,'benchmark'] = self.base.mktprice_close()/init_close
            # print(self.base.eval_date,self.account.account.loc[self.base.eval_date,c.Util.PORTFOLIO_NPV])
            self.base.next()

            if self.base.eval_date.year != eval_year:
                eval_year = self.base.eval_date.year
                self.update_target_option() # Update option at last trading day of the year
                # stop_loss = False
            self.update_maturity()
            # if self.base.is_end_of_quater():
            #     self.update_target_option()

        return self.account

df_base = pd.read_excel('../../../data/中证全指日收盘价.xlsx')
df_base[c.Util.DT_DATE] = df_base['日期'].apply(lambda x:x.date())
df_base = df_base.rename(columns={'000985.CSI': c.Util.AMT_CLOSE})
id_instrument = '000985.CSI'
df_base[c.Util.ID_INSTRUMENT] = id_instrument

sythetic = SytheticOption(df_index=df_base)
sythetic.d = 50
account = sythetic.back_test()
account.account.to_csv('../../accounts_data/sythetic_account.csv')
account.trade_records.to_csv('../../accounts_data/sythetic_records.csv')
res = account.analysis()
print(res)
pu = PlotUtil()
dates = list(account.account.index)
npv = list(account.account[c.Util.PORTFOLIO_NPV])
benchmark = list(account.account['benchmark'])
pu.plot_line_chart(dates, [npv,benchmark], ['npv','benchmark'])

plt.show()

# npvs = []
# df_npvs = pd.DataFrame()
# for d in [30,40,50,60,90]:
#     print(d)
#     sythetic = SytheticOption(df_index=df_base)
#     sythetic.d = d
#     account = sythetic.back_test()
#     npvs.append(list(account.account[c.Util.PORTFOLIO_NPV]))
#     df_npvs['npv '+str(d) + ' day'] = list(account.account[c.Util.PORTFOLIO_NPV])
# df_npvs['dt_date'] = list(account.account.index)
# df_npvs['benchmark'] = list(account.account['benchmark'])
# df_npvs.to_csv('../../accounts_data/df_npvs.csv')
# # pu = PlotUtil()
# # dates = list(account.account.index)
# npvs.append(list(account.account['benchmark']))
# pu.plot_line_chart(dates, npvs, ['npv 30 d','npv 40 d','npv 50 d','npv 60 d','npv 90 d','benchmark'])
# plt.show()
