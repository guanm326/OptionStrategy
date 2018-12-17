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
            self.underlying_unit_ratio = 1
        elif df_future_c1 is not None:
            self.df_base = df_future_c1
            self.underlying = BaseFutureCoutinuous(df_future_c1=df_future_c1, df_futures_all_daily=df_future_all)
            self.underlying.init()
            self.underlying_unit_ratio = 1/1000.0
        self.optionset = BaseOptionSet(df_option)
        self.optionset.init()
        self.account = BaseAccount(c.Util.BILLION / 10)
        self.unit = 50
        self.min_holding = 20
        self.slippage = 0
        self.nbr_maturity = 0
        self.moneyness_rank = 0
        self.m = 1
        self.cd_price = c.CdTradePrice.CLOSE
        self.rf = 0.03

    def prepare_strategy(self):
        t_quote = self.t_quote[(self.t_quote['rank']<=3)&(self.t_quote['rank']>=-3)] # 只考虑三挡以内期权
        df_reverse = t_quote[t_quote['pct_arbitrage_window']>0.005]
        df_conversion = t_quote[t_quote['pct_arbitrage_window']<-0.005]
        reverse = self.max_pair(df_reverse)
        conversion = self.max_pair(df_conversion)
        return reverse, conversion

    def close_signal(self,strategy,cd_strategy):
        discount = c.PricingUtil.get_discount(self.optionset.eval_date, strategy['call'].maturitydt(), self.rf)
        arbitrage_window = strategy['put'].underlying_close() \
                                             + strategy['put'].mktprice_close() - strategy['call'].mktprice_close() \
                                             - strategy['put'].applicable_strike() * discount
        unit = None
        if cd_strategy == 'reverse':
            # id_call = strategy['call'].id_instrument()
            # df_reverse = self.t_quote[self.t_quote[c.Util.ID_CALL] == id_call]
            # print(id_call,self.optionset.eval_date)
            # print(self.t_quote)
            if arbitrage_window<=0 or strategy['call'].maturitydt() == self.optionset.eval_date:
                # reverse 套利平仓
                for option in strategy.values():
                    order = self.account.create_close_order(option, cd_trade_price=self.cd_price)
                    record = option.execute_order(order, slippage=self.slippage)
                    self.account.add_record(record, option)
                    unit = record[c.Util.TRADE_UNIT]
                unit_underlying = np.floor(unit * self.underlying_unit_ratio * strategy['put'].multiplier())
                order = self.account.create_trade_order(self.underlying, c.LongShort.LONG, unit_underlying,
                                                        cd_trade_price=self.cd_price)
                record = self.underlying.execute_order(order, slippage=self.slippage)
                self.account.add_record(record, self.underlying)
                return True
            else:
                return False
        if cd_strategy == 'conversion':
            # id_call = strategy['call'].id_instrument()
            # df_reverse = self.t_quote[self.t_quote[c.Util.ID_CALL] == id_call]
            if arbitrage_window>=0 or strategy['call'].maturitydt() == self.optionset.eval_date:
                # conversion 套利平仓
                for option in strategy.values():
                    order = self.account.create_close_order(option, cd_trade_price=self.cd_price)
                    record = option.execute_order(order, slippage=self.slippage)
                    self.account.add_record(record, option)
                    unit = record[c.Util.TRADE_UNIT]
                unit_underlying = np.floor(unit * self.underlying_unit_ratio * strategy['put'].multiplier())
                order = self.account.create_trade_order(self.underlying, c.LongShort.SHORT, unit_underlying,
                                                        cd_trade_price=self.cd_price)
                record = self.underlying.execute_order(order, slippage=self.slippage)
                self.account.add_record(record, self.underlying)
                return True
            else:
                return False

    def max_pair(self,df):
        if df.empty or len(df) == 0: return
        row = df.loc[df['pct_arbitrage_window'].idxmax()]
        option_call = self.optionset.get_baseoption_by_id(row[c.Util.ID_CALL])
        option_put = self.optionset.get_baseoption_by_id(row[c.Util.ID_PUT])
        strategy = {'call':option_call,'put':option_put}
        return strategy

    def excute_box(self,box):
        reverse, conversion = box
        if reverse is not None and conversion is not None:
            for cd_option in reverse.keys():
                # short put; buy call
                option = reverse[cd_option]
                if cd_option == 'call':
                    long_short = c.LongShort.LONG
                else:
                    long_short = c.LongShort.SHORT
                order = self.account.create_trade_order(option, long_short, self.unit,
                                                        cd_trade_price=self.cd_price)
                record = option.execute_order(order, slippage=self.slippage)
                self.account.add_record(record, option)
            for cd_option in conversion.keys():
                # long put; short call
                option = conversion[cd_option]
                if cd_option == 'call':
                    long_short = c.LongShort.SHORT
                else:
                    long_short = c.LongShort.LONG
                order = self.account.create_trade_order(option, long_short, self.unit,
                                                        cd_trade_price=self.cd_price)
                record = option.execute_order(order, slippage=self.slippage)
                self.account.add_record(record, option)

    def open_reverse(self,strategy):
        # short underlying, put; buy call
        if strategy is None: return False
        for cd_option in strategy.keys():
            option = strategy[cd_option]
            if cd_option == 'call': long_short = c.LongShort.LONG
            else: long_short = c.LongShort.SHORT
            order = self.account.create_trade_order(option, long_short, self.unit,
                                                    cd_trade_price=self.cd_price)
            record = option.execute_order(order, slippage=self.slippage)
            self.account.add_record(record, option)
        unit_underlying = np.floor(self.unit * self.underlying_unit_ratio * strategy['put'].multiplier())
        order = self.account.create_trade_order(self.underlying, c.LongShort.SHORT, unit_underlying,
                                                cd_trade_price=self.cd_price)
        record = self.underlying.execute_order(order, slippage=self.slippage)
        self.account.add_record(record, self.underlying)
        return True

    def excute_conversion(self,strategy):
        # long underlying, put; short call
        if strategy is None: return False
        for cd_option in strategy.keys():
            option = strategy[cd_option]
            if cd_option == 'call': long_short = c.LongShort.SHORT
            else: long_short = c.LongShort.LONG
            order = self.account.create_trade_order(option, long_short, self.unit,
                                                    cd_trade_price=self.cd_price)
            record = option.execute_order(order, slippage=self.slippage)
            self.account.add_record(record, option)
        unit_underlying = np.floor(self.unit * self.underlying_unit_ratio * strategy['put'].multiplier())
        order = self.account.create_trade_order(self.underlying, c.LongShort.LONG, unit_underlying,
                                                cd_trade_price=self.cd_price)
        record = self.underlying.execute_order(order, slippage=self.slippage)
        self.account.add_record(record, self.underlying)
        return True

    def update_arbitrage_window(self):
        dt_maturity = self.optionset.select_maturity_date(nbr_maturity=0, min_holding=1)
        t_qupte = self.optionset.get_T_quotes(dt_maturity, self.cd_price)
        t_qupte.loc[:, 'diff'] = abs(
            t_qupte.loc[:, c.Util.AMT_APPLICABLE_STRIKE] - t_qupte.loc[:, c.Util.AMT_UNDERLYING_CLOSE])
        idx_atm = t_qupte['diff'].idxmin()
        t_qupte.loc[:, 'rank'] = t_qupte.index - idx_atm
        discount = c.PricingUtil.get_discount(self.optionset.eval_date, dt_maturity, self.rf)
        t_qupte.loc[:,'arbitrage_window'] = t_qupte.loc[:,c.Util.AMT_UNDERLYING_CLOSE]\
                                            + t_qupte.loc[:,c.Util.AMT_PUT_QUOTE] - t_qupte.loc[:,c.Util.AMT_CALL_QUOTE]\
                                            - t_qupte.loc[:,c.Util.AMT_APPLICABLE_STRIKE]*discount
        # t_qupte.loc[:, 'arbitrage_window'] = self.underlying.mktprice_close() \
        #                                      + t_qupte.loc[:, c.Util.AMT_PUT_QUOTE] - t_qupte.loc[:,
        #                                                                               c.Util.AMT_CALL_QUOTE] \
        #                                      - t_qupte.loc[:, c.Util.AMT_APPLICABLE_STRIKE] * discount
        t_qupte.loc[:, 'pct_arbitrage_window'] = t_qupte.loc[:,'arbitrage_window']/t_qupte.loc[:,c.Util.AMT_UNDERLYING_CLOSE]
        self.t_quote = t_qupte
        self.unit = self.account.portfolio_total_value/t_qupte.loc[:,c.Util.AMT_UNDERLYING_CLOSE].values[0]/10000


    def back_test(self):
        cd_strategy = 'reverse'# Reverse
        empty_position = True
        strategy_excuted = None
        while self.optionset.has_next():
            if self.optionset.eval_date == datetime.date(2015,6,24):
                print('')
            self.update_arbitrage_window()
            if empty_position:
                reverse, conversion = self.prepare_strategy()
                empty_position = not self.open_reverse(reverse)
                strategy_excuted = reverse
            else:
                empty_position = self.close_signal(strategy_excuted,cd_strategy)
            self.underlying.shift_contract_month(self.account,self.slippage)
            self.account.daily_accounting(self.optionset.eval_date)
            self.optionset.next()
            self.underlying.next()
        return self.account

start_date = datetime.date(2015, 5, 1)
end_date = datetime.date(2015, 8, 30)
df_metrics = get_data.get_50option_mktdata(start_date, end_date)
df_f_c1 = get_data.get_mktdata_future_c1_daily(start_date,end_date,c.Util.STR_IH)
df_f_all = get_data.get_future_mktdata(start_date,end_date,c.Util.STR_IH)
parity = ParityArbitrage(df_metrics,df_future_c1=df_f_c1,df_future_all=df_f_all)
account = parity.back_test()
account.account.to_csv('../../accounts_data/ParityArbitrage-account.csv')
account.trade_records.to_csv('../../accounts_data/ParityArbitrage-records.csv')
print(account.account)
print(account.trade_records)