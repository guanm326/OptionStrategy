from back_test.model.base_instrument import BaseInstrument
from back_test.model.base_future_coutinuous import BaseFutureCoutinuous
from back_test.model.base_option_set import BaseOptionSet
import back_test.model.constant as c
from back_test.model.base_account import BaseAccount
import data_access.get_data as get_data
from PricingLibrary.BlackCalculator import BlackCalculator
from PricingLibrary.Options import EuropeanOption
from OptionStrategyLib.VolatilityModel.historical_volatility import HistoricalVolatilityModels as histvol
from Utilities.PlotUtil import PlotUtil
import matplotlib.pyplot as plt
import datetime
import pandas as pd
import numpy as np
import math


class ParityArbitrage(object):
    def __init__(self, df_option, df_index=None, df_future_c1=None, df_future_all=None):
        if df_index is not None:
            self.df_base = df_index
            self.underlying = BaseInstrument(df_index)
            self.underlying.init()
        elif df_future_c1 is not None:
            self.df_base = df_future_c1
            self.underlying = BaseFutureCoutinuous(df_future_c1=df_future_c1, df_futures_all_daily=df_future_all)
            self.underlying.init()
        self.optionset = BaseOptionSet(df_option)
        self.optionset.init()
        self.account = BaseAccount(c.Util.BILLION / 100)
        self.unit = 500
        self.min_holding = 20
        self.slippage = 0
        self.nbr_maturity = 0
        self.moneyness_rank = 0
        self.m = 1
        self.cd_price = c.CdTradePrice.CLOSE
        self.rf = 0.03

    def open_signal(self):
        df_reverse = self.t_quote[self.t_quote['pct_arbitrage_window']>0.005]
        df_conversion = self.t_quote[self.t_quote['pct_arbitrage_window']<-0.005]
        reverse = self.max_pair(df_reverse)
        conversion = self.max_pair(df_conversion)
        return reverse, conversion

    def max_pair(self,df):
        if len(df) == 0: return
        row = df[df['pct_arbitrage_window'].idxmax()]
        option_call = self.optionset.get_baseoption_by_id(row[c.Util.ID_CALL])
        option_put = self.optionset.get_baseoption_by_id(row[c.Util.ID_PUT])
        strategy = [{'call':option_call,'put':option_put}]
        return strategy

    def excute_reverse(self,dict):
        # short underlying, put; buy call
        if dict is None: return
        for cd_option in dict.keys():
            option = dict[cd_option]
            if cd_option == 'call': long_short = c.LongShort.LONG
            else: long_short = c.LongShort.SHORT
            order = self.account.create_trade_order(option, long_short, self.unit,
                                                    cd_trade_price=self.cd_price)
            record = option.execute_order(order, slippage=self.slippage)
            self.account.add_record(record, option)

    def arbitrage_window(self):
        dt_maturity = self.optionset.select_maturity_date(nbr_maturity=1, min_holding=self.min_holding)
        t_qupte = self.optionset.get_T_quotes(dt_maturity, self.cd_price)
        t_qupte.loc[:, 'diff'] = abs(
            t_qupte.loc[:, c.Util.AMT_APPLICABLE_STRIKE] - t_qupte.loc[:, c.Util.AMT_UNDERLYING_CLOSE])
        idx_atm = t_qupte['diff'].idxmin()
        t_qupte.loc[:, 'rank'] = t_qupte.index - idx_atm
        t_qupte = t_qupte[(t_qupte['rank']<=3)&(t_qupte['rank']>=-3)]
        discount = c.PricingUtil.get_discount(self.optionset.eval_date, dt_maturity, self.rf)
        t_qupte.loc[:,'arbitrage_window'] = t_qupte.loc[:,c.Util.AMT_UNDERLYING_CLOSE]\
                                            + t_qupte.loc[:,c.Util.AMT_PUT_QUOTE] - t_qupte.loc[:,c.Util.AMT_CALL_QUOTE]\
                                            - t_qupte.loc[:,c.Util.AMT_STRIKE]*discount
        t_qupte.loc[:, 'pct_arbitrage_window'] = t_qupte.loc[:,'arbitrage_window']/t_qupte.loc[:,c.Util.AMT_UNDERLYING_CLOSE]
        self.t_quote = t_qupte
        # return t_qupte


start_date = datetime.date(2018, 11, 1)
end_date = datetime.date(2018, 12, 1)
df_metrics = get_data.get_50option_mktdata(start_date, end_date)
parity = ParityArbitrage(df_metrics)
parity.arbitrage_window()