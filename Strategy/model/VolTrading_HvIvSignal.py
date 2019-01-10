from back_test.model.base_option_set import BaseOptionSet
from back_test.model.base_option import BaseOption
from back_test.model.base_account import BaseAccount
from back_test.model.base_future_coutinuous import BaseFutureCoutinuous
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


class VolTrading(object):
    """
    隐含与历史波动率策略报告原版参数设定
    """
    def __init__(self, start_date, end_date, df_metrics,df_vol,df_future_c1_daily,df_futures_all_daily):
        self.min_holding = 20
        self.slippage = 0
        self.nbr_maturity = 0
        self.moneyness_rank = 0
        self.m = 1
        self.rf = 0.03
        self.h = 90
        self.cd_option_price = c.CdTradePrice.CLOSE
        self.cd_future_price = c.CdTradePrice.CLOSE
        self.cd_price = c.CdPriceType.CLOSE
        df_future_c1_daily['amt_hv'] = histvol.hist_vol(df_future_c1_daily[c.Util.AMT_CLOSE], n=30)
        dt_start = max(df_future_c1_daily[c.Util.DT_DATE].values[0], df_metrics[c.Util.DT_DATE].values[0])
        self.end_date = min(df_future_c1_daily[c.Util.DT_DATE].values[-1], df_metrics[c.Util.DT_DATE].values[-1])
        df_metrics = df_metrics[df_metrics[c.Util.DT_DATE] >= dt_start].reset_index(drop=True)
        df_c1 = df_future_c1_daily[df_future_c1_daily[c.Util.DT_DATE] >= dt_start].reset_index(drop=True)
        df_all = df_futures_all_daily[df_futures_all_daily[c.Util.DT_DATE] >= dt_start].reset_index(drop=True)
        self.df_vol = pd.merge(df_vol, df_future_c1_daily[[c.Util.DT_DATE, 'amt_hv']],on=c.Util.DT_DATE).set_index(c.Util.DT_DATE)
        self.optionset = BaseOptionSet(df_metrics)
        self.optionset.init()
        self.hedging = SytheticOption(df_c1, df_futures_all_daily=df_all)
        self.hedging.init()
        self.account = BaseAccount(init_fund=c.Util.BILLION, leverage=1.0, rf=self.rf)
        self.prepare_timing()

    def prepare_timing(self):
        h = self.h
        self.df_vol['amt_premium'] = self.df_vol[c.Util.PCT_IMPLIED_VOL] - self.df_vol['amt_hv']
        self.df_vol['amt_1std'] = c.Statistics.standard_deviation(self.df_vol['amt_premium'], n=h)
        self.df_vol['amt_2std'] = 2 * c.Statistics.standard_deviation(self.df_vol['amt_premium'], n=h)
        self.df_vol['percentile_95'] = c.Statistics.percentile(self.df_vol[c.Util.PCT_IMPLIED_VOL], n=252, percent=0.95)
        # self.df_vol['amt_premium'] = (self.df_vol['amt_iv'] - self.df_vol['amt_hv']).shift()
        # self.df_vol['amt_iv_previous'] = self.df_vol['amt_iv'].shift()
        # self.df_vol['amt_1std'] = c.Statistics.moving_average(self.df_vol['amt_premium'],
        #                                                       n=h) + c.Statistics.standard_deviation(
        #     self.df_vol['amt_premium'], n=h)
        # self.df_vol['amt_n1std'] = c.Statistics.moving_average(self.df_vol['amt_premium'],
        #                                                        n=h) - c.Statistics.standard_deviation(
        #     self.df_vol['amt_premium'], n=h)
        # self.df_vol['amt_2std'] = c.Statistics.moving_average(self.df_vol['amt_premium'],
        #                                                       n=h) + 2 * c.Statistics.standard_deviation(
        #     self.df_vol['amt_premium'], n=h)
        # self.df_vol['amt_n2std'] = c.Statistics.moving_average(self.df_vol['amt_premium'],
        #                                                        n=h) - 2 * c.Statistics.standard_deviation(
        #     self.df_vol['amt_premium'], n=h)
        # self.df_vol = self.df_vol.set_index(c.Util.DT_DATE)
        # self.df_vol['iv_percentile'] = c.Statistics.standard_deviation(self.df_vol['amt_iv'], n=252)

    def open_signal(self):
        return self.open_signal_ivhv()

    def close_signal(self):
        return self.close_signal_ivhv()

    def open_signal_ivhv(self):
        dt_date = self.optionset.eval_date
        if dt_date not in self.df_vol.index:
            return False
        amt_premium = self.df_vol.loc[dt_date, 'amt_premium']
        amt_1std = self.df_vol.loc[dt_date, 'amt_1std']
        # if amt_premium > amt_1std and amt_premium > 0:
        if amt_premium > amt_1std:
            print(dt_date, ' open position')
            return True
        else:
            return False

    def close_signal_ivhv(self):
        dt_maturity = None
        for option in self.account.dict_holding.values():
            if isinstance(option, BaseOption) and option is not None:
                dt_maturity = option.maturitydt()
                break
        if (dt_maturity - self.optionset.eval_date).days <= 5:
            return True
        dt_date = self.optionset.eval_date
        amt_premium = self.df_vol.loc[dt_date, 'amt_premium']
        # amt_n1std = self.df_vol.loc[dt_date, 'amt_n1std']
        # if amt_premium < amt_n1std or amt_premium <= 0:
        if amt_premium < 0:
            print(dt_date, ' close position')
            return True
        else:
            return False

    def strategy(self):
        return self.short_straddle()

    def short_straddle(self):
        maturity = self.optionset.select_maturity_date(nbr_maturity=self.nbr_maturity, min_holding=self.min_holding)
        list_atm_call, list_atm_put = self.optionset.get_options_list_by_moneyness_mthd1(
            moneyness_rank=self.moneyness_rank,
            maturity=maturity, cd_price=self.cd_price)
        atm_call = self.optionset.select_higher_volume(list_atm_call)
        atm_put = self.optionset.select_higher_volume(list_atm_put)
        if atm_call is None or atm_put is None:
            return
        else:
            return [atm_call, atm_put]

    def excute(self, strategy):
        if strategy is None:
            return False
        else:
            pv = self.account.portfolio_total_value
            self.option_holding = {}
            for option in strategy:
                unit = np.floor(np.floor(pv / option.strike()) / option.multiplier()) * self.m
                order = self.account.create_trade_order(option, c.LongShort.SHORT, unit,
                                                        cd_trade_price=self.cd_option_price)
                record = option.execute_order(order, slippage=self.slippage)
                self.account.add_record(record, option)
                self.option_holding.update({option: unit})
            return True

    def close_out(self):
        close_out_orders = self.account.creat_close_out_order(cd_trade_price=c.CdTradePrice.CLOSE)
        for order in close_out_orders:
            execution_record = self.account.dict_holding[order.id_instrument] \
                .execute_order(order, slippage=self.slippage, execute_type=c.ExecuteType.EXECUTE_ALL_UNITS)
            self.account.add_record(execution_record, self.account.dict_holding[order.id_instrument])

    def close_out_1(self):
        for option in self.account.dict_holding.values():
            if isinstance(option, BaseOption):
                order = self.account.create_close_order(option, cd_trade_price=self.cd_option_price)
            else:
                order = self.account.create_close_order(option, cd_trade_price=self.cd_future_price)
            record = option.execute_order(order, slippage=self.slippage)
            self.account.add_record(record, option)

    def delta_hedge(self):
        option1 = list(self.option_holding.keys())[0]
        iv_htbr = self.optionset.get_iv_by_otm_iv_curve(dt_maturity=option1.maturitydt(),
                                                        strike=option1.applicable_strike())
        options_delta = 0
        for option in self.option_holding.keys():
            unit = self.option_holding[option]
            options_delta += unit * option.get_delta(iv_htbr) * option.multiplier()
        hedge_unit = self.hedging.get_hedge_rebalancing_unit(options_delta, c.BuyWrite.WRITE)
        self.hedging.synthetic_unit += - hedge_unit
        if hedge_unit > 0:
            long_short = c.LongShort.LONG
        else:
            long_short = c.LongShort.SHORT
        order_u = self.account.create_trade_order(self.hedging, long_short, hedge_unit,
                                                  cd_trade_price=self.cd_future_price)
        record_u = self.hedging.execute_order(order_u, slippage=self.slippage)
        self.account.add_record(record_u, self.hedging)
        self.account.daily_accounting(self.optionset.eval_date)

    def back_test(self):
        empty_position = True
        while self.optionset.eval_date <= self.end_date:
            if self.optionset.eval_date >= self.end_date:  # Final close out all.
                self.close_out()
                self.account.daily_accounting(self.optionset.eval_date)
                print(self.optionset.eval_date, ' close out ')
                print(self.optionset.eval_date, self.hedging.eval_date,
                      self.account.account.loc[self.optionset.eval_date, c.Util.PORTFOLIO_NPV],
                      int(self.account.cash))
                break
            # 标的移仓换月
            self.hedging.shift_contract_month(self.account, self.slippage, cd_price=c.CdTradePrice.CLOSE)
            # 平仓
            if not empty_position:
                if self.close_signal():
                    self.close_out_1()
                    empty_position = True
            # 开仓
            if empty_position and self.open_signal():
                s = self.strategy()
                empty_position = not self.excute(s)
            # Delta hedge
            if not empty_position:
                self.delta_hedge()
            self.account.daily_accounting(self.optionset.eval_date)
            if not self.optionset.has_next():
                break
            self.optionset.next()
            self.hedging.next()
        return self.account



dt_start = datetime.date(2016, 12, 31)
dt_end = datetime.date(2017, 12, 31)
dt_histvol = dt_start - datetime.timedelta(days=300)
name_code = c.Util.STR_IH
name_code_option = c.Util.STR_50ETF
df_metrics = get_data.get_50option_mktdata(dt_start, dt_end)
df_future_c1_daily = get_data.get_mktdata_future_c1_daily(dt_histvol, dt_end, name_code)
df_futures_all_daily = get_data.get_mktdata_future_daily(dt_start, dt_end,name_code)
df_iv = get_data.get_iv_by_moneyness(dt_histvol, dt_end, name_code_option)
df_iv = df_iv[df_iv[c.Util.CD_OPTION_TYPE] == 'put_call_htbr'][[c.Util.DT_DATE,c.Util.PCT_IMPLIED_VOL]].reset_index(drop=True)
# df_iv = df_iv.rename(columns={c.Util.PCT_IMPLIED_VOL: 'amt_iv'})
vol_arbitrage = VolTrading(dt_start, dt_end, df_metrics,df_iv,df_future_c1_daily,df_futures_all_daily)

account = vol_arbitrage.back_test()

account.account.to_csv('../iv_hv_account.csv')
account.trade_records.to_csv('../iv_hv_record.csv')
res = account.analysis()
print(res)
pu = PlotUtil()
dates = list(account.account.index)
npv = list(account.account[c.Util.PORTFOLIO_NPV])
pu.plot_line_chart(dates, [npv], ['npv'])

plt.show()