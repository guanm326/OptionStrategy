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
        self.m = 1
        if df_index is not None:
            self.df_base = df_index
            self.underlying = BaseInstrument(df_index)
            self.underlying.init()
            self.underlying_unit_ratio = 1
            self.m = 0.75
        elif df_future_c1 is not None:
            self.df_base = df_future_c1
            self.underlying = BaseFutureCoutinuous(df_future_c1=df_future_c1, df_futures_all_daily=df_future_all)
            self.underlying.init()
            self.underlying_unit_ratio = 1/1000.0
            self.m = 1
        self.optionset = BaseOptionSet(df_option)
        self.optionset.init()
        self.rf = 0.03
        self.account = BaseAccount(c.Util.BILLION / 10,rf=self.rf)
        self.unit = 50
        self.min_holding = 20
        self.slippage = 1/1000.0
        # self.nbr_maturity = 0
        # self.moneyness_rank = 0
        self.cd_price = c.CdTradePrice.CLOSE
        self.df_arbitrage_window = pd.DataFrame()

    def present_arbitrage_window(self):
        t_quote = self.t_quote[(self.t_quote['rank'] <= 3) & (self.t_quote['rank'] >= -3)]  # 只考虑三挡以内期权
        df_reverse = t_quote[t_quote['pct_arbitrage_window'] > 0.0015]
        df_conversion = t_quote[t_quote['pct_arbitrage_window'] < -0.0015]
        window_reverse = None
        window_conversion = None
        if not df_reverse.empty and len(df_reverse) > 0:
            window_reverse = df_reverse.loc[df_reverse['pct_arbitrage_window'].idxmax(),'pct_arbitrage_window']
        if not df_conversion.empty and len(df_conversion) > 0:
            window_conversion = df_conversion.loc[df_conversion['pct_arbitrage_window'].idxmax(),'pct_arbitrage_window']
        self.df_arbitrage_window.loc[self.optionset.eval_date,'window_reverse'] = window_reverse
        self.df_arbitrage_window.loc[self.optionset.eval_date,'window_conversion'] = window_conversion

    def prepare_strategy(self):
        t_quote = self.t_quote[(self.t_quote['rank']<=3)&(self.t_quote['rank']>=-3)] # 只考虑三挡以内期权
        df_reverse = t_quote[t_quote['pct_arbitrage_window']>0.0015]
        df_conversion = t_quote[t_quote['pct_arbitrage_window']<-0.0015]
        reverse = self.max_pair(df_reverse)
        conversion = self.max_pair(df_conversion)
        return reverse, conversion

    def prepare_box(self):
        t_quote = self.t_quote[(self.t_quote['rank']<=3)&(self.t_quote['rank']>=-3)] # 只考虑三挡以内期权
        # df_reverse = t_quote[t_quote['pct_arbitrage_window']>0.0]
        # df_conversion = t_quote[t_quote['pct_arbitrage_window']<-0.0]
        reverse = self.max_pair(t_quote)
        conversion = self.max_pair(t_quote)
        # TODO: DEFINE BOX ARBITRAGE WINDOW
        if reverse['w'] - conversion['w'] > 0.001 or reverse['w'] - conversion['w'] < -0.001:
            print(self.optionset.eval_date,reverse['w'] - conversion['w'])
            return reverse, conversion
        else:
            return None, None

    def get_arbitrage_window(self,strategy,cd_strategy):
        discount = c.PricingUtil.get_discount(self.optionset.eval_date, strategy['call'].maturitydt(), self.rf)
        if cd_strategy == 'reverse':
            if isinstance(self.underlying,BaseFutureCoutinuous):
                arbitrage_window = self.underlying.mktprice_close()/1000.0 \
                                   + strategy['put'].mktprice_close() - strategy['call'].mktprice_close() \
                                   - strategy['put'].applicable_strike() * discount
            else:
                arbitrage_window = strategy['put'].underlying_close() \
                                   + strategy['put'].mktprice_close() - strategy['call'].mktprice_close() \
                                   - strategy['put'].applicable_strike() * discount
            return arbitrage_window
        elif cd_strategy == 'conversion':
            if isinstance(self.underlying,BaseFutureCoutinuous):
                arbitrage_window = self.underlying.mktprice_close()/1000.0 \
                                   + strategy['put'].mktprice_close() - strategy['call'].mktprice_close() \
                                   - strategy['put'].applicable_strike() * discount
            else:
                arbitrage_window = strategy['put'].underlying_close() \
                                   + strategy['put'].mktprice_close() - strategy['call'].mktprice_close() \
                                   - strategy['put'].applicable_strike() * discount
            return arbitrage_window

    def close_signal(self,strategy,cd_strategy):
        # unit = None
        if cd_strategy == 'reverse':
            arbitrage_window = self.get_arbitrage_window(strategy,cd_strategy)
            if arbitrage_window<=0 or strategy['call'].maturitydt() == self.optionset.eval_date:
                # reverse 套利平仓
                for option in strategy.values():
                    order = self.account.create_close_order(option, cd_trade_price=self.cd_price)
                    record = option.execute_order(order, slippage=self.slippage)
                    self.account.add_record(record, option)
                    # unit = record[c.Util.TRADE_UNIT]
                # unit_underlying = np.floor(unit * self.underlying_unit_ratio * strategy[
                #     'put'].multiplier() / self.underlying.multiplier())
                order = self.account.create_trade_order(self.underlying, c.LongShort.LONG, self.unit_underlying,
                                                        cd_trade_price=self.cd_price)
                record = self.underlying.execute_order(order, slippage=self.slippage)
                self.account.add_record(record, self.underlying)
                return True
            else:
                return False
        if cd_strategy == 'conversion':
            arbitrage_window = self.get_arbitrage_window(strategy,cd_strategy)
            if arbitrage_window>=0 or strategy['call'].maturitydt() == self.optionset.eval_date:
                # conversion 套利平仓
                for option in strategy.values():
                    order = self.account.create_close_order(option, cd_trade_price=self.cd_price)
                    record = option.execute_order(order, slippage=self.slippage)
                    self.account.add_record(record, option)
                    # unit = record[c.Util.TRADE_UNIT]
                # unit_underlying = np.floor(unit * self.underlying_unit_ratio * strategy[
                #     'put'].multiplier() / self.underlying.multiplier())
                order = self.account.create_trade_order(self.underlying, c.LongShort.SHORT, self.unit_underlying,
                                                        cd_trade_price=self.cd_price)
                record = self.underlying.execute_order(order, slippage=self.slippage)
                self.account.add_record(record, self.underlying)
                return True
            else:
                return False
        if cd_strategy == 'box':
            reverse, conversion = strategy
            discount_r = c.PricingUtil.get_discount(self.optionset.eval_date, reverse['call'].maturitydt(), self.rf)
            discount_c = c.PricingUtil.get_discount(self.optionset.eval_date, conversion['call'].maturitydt(), self.rf)
            arbitrage_window_r = reverse['put'].underlying_close() \
                               + reverse['put'].mktprice_close() - reverse['call'].mktprice_close() \
                               - reverse['put'].applicable_strike() * discount_r
            arbitrage_window_c = conversion['put'].underlying_close() \
                               + conversion['put'].mktprice_close() - conversion['call'].mktprice_close() \
                               - conversion['put'].applicable_strike() * discount_c
            if arbitrage_window_r <= 0 or arbitrage_window_c >=0 or reverse['call'].maturitydt() == self.optionset.eval_date \
                    or conversion['call'].maturitydt() == self.optionset.eval_date:
                self.close_out()

    def max_pair(self,df):
        if df.empty or len(df) == 0: return
        row = df.loc[df['pct_arbitrage_window'].idxmax()]
        option_call = self.optionset.get_baseoption_by_id(row[c.Util.ID_CALL])
        option_put = self.optionset.get_baseoption_by_id(row[c.Util.ID_PUT])
        strategy = {'call':option_call,'put':option_put,'w':row['pct_arbitrage_window']}
        return strategy

    def open_box(self,box):
        reverse, conversion = box
        if reverse is not None and conversion is not None:
            for cd_option in ['call','put']:
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
            for cd_option in ['call','put']:
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
            return True

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
        self.unit_underlying = np.floor(self.unit * self.underlying_unit_ratio * strategy['put'].multiplier()/self.underlying.multiplier())
        order = self.account.create_trade_order(self.underlying, c.LongShort.SHORT, self.unit_underlying,
                                                cd_trade_price=self.cd_price)
        record = self.underlying.execute_order(order, slippage=self.slippage)
        self.account.add_record(record, self.underlying)
        return True

    def open_conversion(self,strategy):
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
        self.unit_underlying = np.floor(self.unit * self.underlying_unit_ratio * strategy['put'].multiplier()/self.underlying.multiplier())
        order = self.account.create_trade_order(self.underlying, c.LongShort.LONG, self.unit_underlying,
                                                cd_trade_price=self.cd_price)
        record = self.underlying.execute_order(order, slippage=self.slippage)
        self.account.add_record(record, self.underlying)
        return True

    def update_arbitrage_window(self):
        df = pd.DataFrame()
        for nbr in [0,1]:
            dt_maturity = self.optionset.select_maturity_date(nbr_maturity=nbr, min_holding=1)
            t_qupte = self.optionset.get_T_quotes(dt_maturity, self.cd_price)
            t_qupte.loc[:, 'diff'] = abs(
                t_qupte.loc[:, c.Util.AMT_APPLICABLE_STRIKE] - t_qupte.loc[:, c.Util.AMT_UNDERLYING_CLOSE])
            t_qupte.loc[:, 'rank'] = t_qupte.index - t_qupte['diff'].idxmin()
            discount = c.PricingUtil.get_discount(self.optionset.eval_date, dt_maturity, self.rf)
            if isinstance(self.underlying,BaseInstrument):
                t_qupte.loc[:,'arbitrage_window'] = t_qupte.loc[:, c.Util.AMT_UNDERLYING_CLOSE]\
                                                    + t_qupte.loc[:, c.Util.AMT_PUT_QUOTE] - t_qupte.loc[:, c.Util.AMT_CALL_QUOTE]\
                                                    - t_qupte.loc[:, c.Util.AMT_APPLICABLE_STRIKE]*discount
            else:
                t_qupte.loc[:, 'arbitrage_window'] = self.underlying.mktprice_close()/1000.0 \
                                                     + t_qupte.loc[:, c.Util.AMT_PUT_QUOTE] - t_qupte.loc[:, c.Util.AMT_CALL_QUOTE] \
                                                     - t_qupte.loc[:, c.Util.AMT_APPLICABLE_STRIKE] * discount
            if df.empty:
                df = t_qupte
            else:
                df = df.append(t_qupte,ignore_index=True)
        df.loc[:, 'pct_arbitrage_window'] = df.loc[:,'arbitrage_window']/df.loc[:,c.Util.AMT_UNDERLYING_CLOSE]
        self.t_quote = df
        self.unit = self.m*np.floor(self.account.portfolio_total_value/df.loc[:,c.Util.AMT_UNDERLYING_CLOSE].values[0]/10000)

    def close_out(self):
        close_out_orders = self.account.creat_close_out_order(cd_trade_price=c.CdTradePrice.CLOSE)
        for order in close_out_orders:
            execution_record = self.account.dict_holding[order.id_instrument] \
                .execute_order(order, slippage=self.slippage, execute_type=c.ExecuteType.EXECUTE_ALL_UNITS)
            self.account.add_record(execution_record, self.account.dict_holding[order.id_instrument])

    def back_test(self):
        while self.optionset.has_next():
            self.update_arbitrage_window()
            self.present_arbitrage_window()
            self.optionset.next()
            self.underlying.next()
        return self.df_arbitrage_window

    def back_test_r(self):
        cd_strategy = 'reverse'# Reverse
        empty_position = True
        strategy_excuted = None
        while self.optionset.has_next():
            # if self.underlying.eval_date == datetime.date(2016,11,23):
            #     print('')
            # if self.underlying.eval_date == datetime.date(2016,12,13):
            #     print('')
            self.update_arbitrage_window()
            if empty_position:
                reverse, conversion = self.prepare_strategy()
                empty_position = not self.open_reverse(reverse)
                strategy_excuted = reverse
            else:
                empty_position = self.close_signal(strategy_excuted,cd_strategy)
            if isinstance(self.underlying,BaseFutureCoutinuous):
                self.underlying.shift_contract_month(self.account,self.slippage)
            self.account.daily_accounting(self.optionset.eval_date)
            self.optionset.next()
            self.underlying.next()
        return self.account

    def back_test_c(self):
        cd_strategy = 'conversion'# Reverse
        empty_position = True
        strategy_excuted = None
        while self.optionset.has_next():
            # if self.underlying.eval_date == datetime.date(2016,11,23):
            #     print('')
            # if self.underlying.eval_date == datetime.date(2016,12,13):
            #     print('')
            self.update_arbitrage_window()
            if empty_position:
                reverse, conversion = self.prepare_strategy()
                empty_position = not self.open_conversion(conversion)
                strategy_excuted = conversion
            else:
                empty_position = self.close_signal(strategy_excuted,cd_strategy)
            if isinstance(self.underlying,BaseFutureCoutinuous):
                self.underlying.shift_contract_month(self.account,self.slippage)
            self.account.daily_accounting(self.optionset.eval_date)
            self.optionset.next()
            self.underlying.next()
        return self.account

    def back_test_b(self):
        cd_strategy = 'box'# Box
        empty_position = True
        box = None
        while self.optionset.has_next():
            self.update_arbitrage_window()
            if empty_position:
                box = self.prepare_box()
                empty_position = not self.open_box(box)
            else:
                empty_position = self.close_signal(box,cd_strategy)
            if isinstance(self.underlying,BaseFutureCoutinuous):
                self.underlying.shift_contract_month(self.account,self.slippage)
            self.account.daily_accounting(self.optionset.eval_date)
            self.optionset.next()
            self.underlying.next()
        return self.account

start_date = datetime.date(2015, 2, 9)
# start_date = datetime.date(2015, 5, 1)
# end_date = datetime.date.today()
end_date = datetime.date(2016,1,1)
df_metrics = get_data.get_50option_mktdata(start_date, end_date)
df_index = get_data.get_index_mktdata(start_date,end_date,c.Util.STR_INDEX_50ETF)
parity = ParityArbitrage(df_metrics,df_index=df_index)
# df_f_c1 = get_data.get_mktdata_future_c1_daily(start_date,end_date,c.Util.STR_IH)
# df_f_all = get_data.get_future_mktdata(start_date,end_date,c.Util.STR_IH)
# parity = ParityArbitrage(df_metrics,df_future_c1=df_f_c1,df_future_all=df_f_all)
# df = parity.back_test()
# df.to_csv('../../accounts_data/ParityArbitrage-window.csv')
# account = parity.back_test_r()
account = parity.back_test_b()
account.account.to_csv('../../accounts_data/ParityArbitrage-account.csv')
account.trade_records.to_csv('../../accounts_data/ParityArbitrage-records.csv')
print(account.trade_records)
res = account.analysis()
print(res)
pu = PlotUtil()
dates = list(account.account.index)
npv = list(account.account[c.Util.PORTFOLIO_NPV])
pu.plot_line_chart(dates, [npv], ['npv'])

plt.show()