import datetime
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import back_test.model.constant as c
from Utilities.PlotUtil import PlotUtil
from back_test.model.base_account import BaseAccount
from back_test.model.base_future_coutinuous import BaseFutureCoutinuous
from back_test.model.base_instrument import BaseInstrument
from back_test.model.base_option_set import BaseOptionSet

# class ParityArbitrage1(object):
#     def __init__(self, df_option, df_index, df_future_c1=None, df_future_all=None,df_index1=None):
#         self.m = 1
#         if df_future_c1 is not None:
#             self.df_base = df_future_c1
#             self.underlying = BaseFutureCoutinuous(df_future_c1=df_future_c1, df_futures_all_daily=df_future_all)
#             self.underlying.init()
#             self.base_index = BaseInstrument(df_index)
#             self.base_index.init()
#             self.underlying_unit_ratio = 1/1000.0
#             self.m = 1
#         elif df_index is not None:
#             self.df_base = df_index
#             self.underlying = BaseInstrument(df_index)
#             self.underlying.init()
#             self.underlying_unit_ratio = 1
#             self.m = 0.75
#         if df_index1 is not None:
#             self.base_index_1 = BaseInstrument(df_index1)
#             self.base_index_1.init()
#         self.optionset = BaseOptionSet(df_option)
#         self.optionset.init()
#         self.rf = 0.024
#         self.account = BaseAccount(c.Util.BILLION / 10,rf=self.rf)
#         self.unit = 50
#         self.min_holding = 20
#         self.slippage = 1/1000.0
#         # self.nbr_maturity = 0
#         # self.moneyness_rank = 0
#         self.cd_price = c.CdTradePrice.CLOSE
#         self.df_arbitrage_window = pd.DataFrame()
#
#     def present_arbitrage_window(self):
#         t_quote = self.t_quote[(self.t_quote['rank'] <= 3) & (self.t_quote['rank'] >= -3)]  # 只考虑三挡以内期权
#         df_reverse = t_quote[t_quote['pct_arbitrage_window'] > 0.0015]
#         df_conversion = t_quote[t_quote['pct_arbitrage_window'] < -0.0015]
#         window_reverse = None
#         window_conversion = None
#         if not df_reverse.empty and len(df_reverse) > 0:
#             window_reverse = df_reverse.loc[df_reverse['pct_arbitrage_window'].idxmax(),'pct_arbitrage_window']
#         if not df_conversion.empty and len(df_conversion) > 0:
#             window_conversion = df_conversion.loc[df_conversion['pct_arbitrage_window'].idxmax(),'pct_arbitrage_window']
#         basis_etf = (self.base_index.mktprice_close()*1000-self.underlying.mktprice_close())/(self.base_index.mktprice_close()*1000)
#         basis_index = (self.base_index_1.mktprice_close()-self.underlying.mktprice_close())/self.base_index_1.mktprice_close()
#         self.df_arbitrage_window.loc[self.optionset.eval_date,'window_reverse'] = window_reverse
#         self.df_arbitrage_window.loc[self.optionset.eval_date,'window_conversion'] = window_conversion
#         self.df_arbitrage_window.loc[self.optionset.eval_date,'basis_to_etf'] = basis_etf
#         self.df_arbitrage_window.loc[self.optionset.eval_date,'basis_to_index'] = basis_index
#         self.df_arbitrage_window.loc[self.optionset.eval_date,'50etf'] = self.base_index.mktprice_close()
#         self.df_arbitrage_window.loc[self.optionset.eval_date,'ih'] = self.underlying.mktprice_close()
#         self.df_arbitrage_window.loc[self.optionset.eval_date,'index_50'] = self.base_index_1.mktprice_close()
#         self.df_arbitrage_window.loc[self.optionset.eval_date,'sythetic_underlying_max'] = t_quote.loc[t_quote['sythetic_underlying'].idxmax(),'sythetic_underlying']
#         self.df_arbitrage_window.loc[self.optionset.eval_date,'sythetic_underlying_min'] = t_quote.loc[t_quote['sythetic_underlying'].idxmin(),'sythetic_underlying']
#
#     def prepare_strategy(self):
#         t_quote = self.t_quote[(self.t_quote['rank']<=3)&(self.t_quote['rank']>=-3)] # 只考虑三挡以内期权
#         df_reverse = t_quote[t_quote['pct_arbitrage_window']>0.0015]
#         df_conversion = t_quote[t_quote['pct_arbitrage_window']<-0.0015]
#         reverse, conversion = None, None
#         if not df_reverse.empty or len(df_reverse) > 0:
#             row = df_reverse.loc[df_reverse['pct_arbitrage_window'].idxmax()]
#             reverse = self._pair_strategy(row)
#         if not df_conversion.empty or len(df_conversion) > 0:
#             row = df_conversion.loc[df_conversion['pct_arbitrage_window'].idxmin()]
#             conversion = self._pair_strategy(row)
#         return reverse, conversion
#
#     def prepare_box(self):
#         t_quote = self.t_quote[(self.t_quote['rank']<=3)&(self.t_quote['rank']>=-3)] # 只考虑三挡以内期权
#         reverse = self._pair_strategy_box(t_quote.loc[t_quote['pct_arbitrage_window'].idxmax()])
#         conversion = self._pair_strategy_box(t_quote.loc[t_quote['pct_arbitrage_window'].idxmin()])
#         # TODO: DEFINE BOX ARBITRAGE WINDOW
#         if reverse['w'] >= 0.0 and conversion['w']<=0.0:
#             return reverse, conversion
#         else:
#             return None, None
#
#     def get_arbitrage_window(self,strategy,cd_strategy):
#         discount = c.PricingUtil.get_discount(self.optionset.eval_date, strategy['call'].maturitydt(), self.rf)
#         if cd_strategy == 'reverse':
#             if isinstance(self.underlying,BaseFutureCoutinuous):
#                 arbitrage_window = self.underlying.mktprice_close()/1000.0 \
#                                    + strategy['put'].mktprice_close() - strategy['call'].mktprice_close() \
#                                    - strategy['put'].applicable_strike() * discount
#             else:
#                 arbitrage_window = strategy['put'].underlying_close() \
#                                    + strategy['put'].mktprice_close() - strategy['call'].mktprice_close() \
#                                    - strategy['put'].applicable_strike() * discount
#             return arbitrage_window
#         elif cd_strategy == 'conversion':
#             if isinstance(self.underlying,BaseFutureCoutinuous):
#                 arbitrage_window = self.underlying.mktprice_close()/1000.0 \
#                                    + strategy['put'].mktprice_close() - strategy['call'].mktprice_close() \
#                                    - strategy['put'].applicable_strike() * discount
#             else:
#                 arbitrage_window = strategy['put'].underlying_close() \
#                                    + strategy['put'].mktprice_close() - strategy['call'].mktprice_close() \
#                                    - strategy['put'].applicable_strike() * discount
#             return arbitrage_window
#
#     def close_signal(self,strategy,cd_strategy):
#         # unit = None
#         if cd_strategy == 'reverse':
#             arbitrage_window = self.get_arbitrage_window(strategy,cd_strategy)
#             if arbitrage_window<=0 or strategy['call'].maturitydt() == self.optionset.eval_date:
#                 # reverse 套利平仓
#                 for option in strategy.values():
#                     order = self.account.create_close_order(option, cd_trade_price=self.cd_price)
#                     record = option.execute_order(order, slippage=self.slippage)
#                     self.account.add_record(record, option)
#                     # unit = record[c.Util.TRADE_UNIT]
#                 # unit_underlying = np.floor(unit * self.underlying_unit_ratio * strategy[
#                 #     'put'].multiplier() / self.underlying.multiplier())
#                 order = self.account.create_trade_order(self.underlying, c.LongShort.LONG, self.unit_underlying,
#                                                         cd_trade_price=self.cd_price)
#                 record = self.underlying.execute_order(order, slippage=self.slippage)
#                 self.account.add_record(record, self.underlying)
#                 return True
#             else:
#                 return False
#         if cd_strategy == 'conversion':
#             arbitrage_window = self.get_arbitrage_window(strategy,cd_strategy)
#             if arbitrage_window>=0 or strategy['call'].maturitydt() == self.optionset.eval_date:
#                 # conversion 套利平仓
#                 for option in strategy.values():
#                     order = self.account.create_close_order(option, cd_trade_price=self.cd_price)
#                     record = option.execute_order(order, slippage=self.slippage)
#                     self.account.add_record(record, option)
#                     # unit = record[c.Util.TRADE_UNIT]
#                 # unit_underlying = np.floor(unit * self.underlying_unit_ratio * strategy[
#                 #     'put'].multiplier() / self.underlying.multiplier())
#                 order = self.account.create_trade_order(self.underlying, c.LongShort.SHORT, self.unit_underlying,
#                                                         cd_trade_price=self.cd_price)
#                 record = self.underlying.execute_order(order, slippage=self.slippage)
#                 self.account.add_record(record, self.underlying)
#                 return True
#             else:
#                 return False
#         if cd_strategy == 'box':
#             reverse, conversion = strategy
#             discount_r = c.PricingUtil.get_discount(self.optionset.eval_date, reverse['call'].maturitydt(), self.rf)
#             discount_c = c.PricingUtil.get_discount(self.optionset.eval_date, conversion['call'].maturitydt(), self.rf)
#             arbitrage_window_r = reverse['put'].underlying_close() \
#                                + reverse['put'].mktprice_close() - reverse['call'].mktprice_close() \
#                                - reverse['put'].applicable_strike() * discount_r
#             arbitrage_window_c = conversion['put'].underlying_close() \
#                                + conversion['put'].mktprice_close() - conversion['call'].mktprice_close() \
#                                - conversion['put'].applicable_strike() * discount_c
#             if arbitrage_window_r <= 0 or arbitrage_window_c >=0 or reverse['call'].maturitydt() == self.optionset.eval_date \
#                     or conversion['call'].maturitydt() == self.optionset.eval_date:
#                 self.close_out()
#                 return True
#             else:
#                 return False
#
#     # def max_pair(self,df):
#     #     if df.empty or len(df) == 0: return
#     #     row = df.loc[df['pct_arbitrage_window'].idxmax()]
#     #     option_call = self.optionset.get_baseoption_by_id(row[c.Util.ID_CALL])
#     #     option_put = self.optionset.get_baseoption_by_id(row[c.Util.ID_PUT])
#     #     strategy = {'call':option_call,'put':option_put,'w':row['pct_arbitrage_window']}
#     #     return strategy
#
#     def _pair_strategy(self,row):
#         option_call = self.optionset.get_baseoption_by_id(row[c.Util.ID_CALL])
#         option_put = self.optionset.get_baseoption_by_id(row[c.Util.ID_PUT])
#         strategy = {'call':option_call,'put':option_put}
#         return strategy
#
#     def _pair_strategy_box(self,row):
#         option_call = self.optionset.get_baseoption_by_id(row[c.Util.ID_CALL])
#         option_put = self.optionset.get_baseoption_by_id(row[c.Util.ID_PUT])
#         strategy = {'call':option_call,'put':option_put,'w':row['pct_arbitrage_window']}
#         return strategy
#
#
#     def open_box(self,box):
#         reverse, conversion = box
#         if reverse is not None and conversion is not None:
#             for cd_option in ['call','put']:
#                 # short put; buy call
#                 option = reverse[cd_option]
#                 if cd_option == 'call':
#                     long_short = c.LongShort.LONG
#                 else:
#                     long_short = c.LongShort.SHORT
#                 order = self.account.create_trade_order(option, long_short, self.unit,
#                                                         cd_trade_price=self.cd_price)
#                 record = option.execute_order(order, slippage=self.slippage)
#                 self.account.add_record(record, option)
#             for cd_option in ['call','put']:
#                 # long put; short call
#                 option = conversion[cd_option]
#                 if cd_option == 'call':
#                     long_short = c.LongShort.SHORT
#                 else:
#                     long_short = c.LongShort.LONG
#                 order = self.account.create_trade_order(option, long_short, self.unit,
#                                                         cd_trade_price=self.cd_price)
#                 record = option.execute_order(order, slippage=self.slippage)
#                 self.account.add_record(record, option)
#             return True
#         else:
#             return False
#
#     def open_reverse(self,strategy):
#         # short underlying, put; buy call
#         if strategy is None: return False
#         for cd_option in ['call','put']:
#             option = strategy[cd_option]
#             if cd_option == 'call': long_short = c.LongShort.LONG
#             else: long_short = c.LongShort.SHORT
#             order = self.account.create_trade_order(option, long_short, self.unit,
#                                                     cd_trade_price=self.cd_price)
#             record = option.execute_order(order, slippage=self.slippage)
#             self.account.add_record(record, option)
#         self.unit_underlying = np.floor(self.unit * self.underlying_unit_ratio * strategy['put'].multiplier()/self.underlying.multiplier())
#         order = self.account.create_trade_order(self.underlying, c.LongShort.SHORT, self.unit_underlying,
#                                                 cd_trade_price=self.cd_price)
#         record = self.underlying.execute_order(order, slippage=self.slippage)
#         self.account.add_record(record, self.underlying)
#         return True
#
#     def open_conversion(self,strategy):
#         # long underlying, put; short call
#         if strategy is None: return False
#         for cd_option in ['call','put']:
#             option = strategy[cd_option]
#             if cd_option == 'call': long_short = c.LongShort.SHORT
#             else: long_short = c.LongShort.LONG
#             order = self.account.create_trade_order(option, long_short, self.unit,
#                                                     cd_trade_price=self.cd_price)
#             record = option.execute_order(order, slippage=self.slippage)
#             self.account.add_record(record, option)
#         self.unit_underlying = np.floor(self.unit * self.underlying_unit_ratio * strategy['put'].multiplier()/self.underlying.multiplier())
#         order = self.account.create_trade_order(self.underlying, c.LongShort.LONG, self.unit_underlying,
#                                                 cd_trade_price=self.cd_price)
#         record = self.underlying.execute_order(order, slippage=self.slippage)
#         self.account.add_record(record, self.underlying)
#         return True
#
#     def update_arbitrage_window(self):
#         df = pd.DataFrame()
#         for nbr in [0]:
#             dt_maturity = self.optionset.select_maturity_date(nbr_maturity=nbr, min_holding=1)
#             t_qupte = self.optionset.get_T_quotes(dt_maturity, self.cd_price)
#             t_qupte.loc[:, 'diff'] = abs(
#                 t_qupte.loc[:, c.Util.AMT_APPLICABLE_STRIKE] - t_qupte.loc[:, c.Util.AMT_UNDERLYING_CLOSE])
#             t_qupte.loc[:, 'rank'] = t_qupte.index - t_qupte['diff'].idxmin()
#             discount = c.PricingUtil.get_discount(self.optionset.eval_date, dt_maturity, self.rf)
#             t_qupte.loc[:, 'sythetic_underlying'] = t_qupte.loc[:,c.Util.AMT_CALL_QUOTE] - t_qupte.loc[:,c.Util.AMT_PUT_QUOTE] + t_qupte.loc[:, c.Util.AMT_APPLICABLE_STRIKE]*discount
#             if isinstance(self.underlying,BaseInstrument):
#                 t_qupte.loc[:,'arbitrage_window'] = t_qupte.loc[:, c.Util.AMT_UNDERLYING_CLOSE]\
#                                                     + t_qupte.loc[:, c.Util.AMT_PUT_QUOTE] - t_qupte.loc[:, c.Util.AMT_CALL_QUOTE]\
#                                                     - t_qupte.loc[:, c.Util.AMT_APPLICABLE_STRIKE]*discount
#             else:
#                 t_qupte.loc[:, 'arbitrage_window'] = self.underlying.mktprice_close()/1000.0 \
#                                                      + t_qupte.loc[:, c.Util.AMT_PUT_QUOTE] - t_qupte.loc[:, c.Util.AMT_CALL_QUOTE] \
#                                                      - t_qupte.loc[:, c.Util.AMT_APPLICABLE_STRIKE] * discount
#             if df.empty:
#                 df = t_qupte
#             else:
#                 df = df.append(t_qupte,ignore_index=True)
#         df.loc[:, 'pct_arbitrage_window'] = df.loc[:,'arbitrage_window']/df.loc[:,c.Util.AMT_UNDERLYING_CLOSE]
#         self.t_quote = df
#         self.unit = self.m*np.floor(self.account.portfolio_total_value/df.loc[:,c.Util.AMT_UNDERLYING_CLOSE].values[0]/10000)
#
#     def close_out(self):
#         close_out_orders = self.account.creat_close_out_order(cd_trade_price=c.CdTradePrice.CLOSE)
#         for order in close_out_orders:
#             execution_record = self.account.dict_holding[order.id_instrument] \
#                 .execute_order(order, slippage=self.slippage, execute_type=c.ExecuteType.EXECUTE_ALL_UNITS)
#             self.account.add_record(execution_record, self.account.dict_holding[order.id_instrument])
#
#     def back_test(self):
#         while self.optionset.has_next():
#             self.update_arbitrage_window()
#             self.present_arbitrage_window()
#             self.optionset.next()
#             self.underlying.next()
#             if isinstance(self.underlying, BaseFutureCoutinuous):
#                 self.base_index_1.next()
#                 self.base_index.next()
#         return self.df_arbitrage_window
#
#     def back_test_r(self):
#         cd_strategy = 'reverse'# Reverse
#         empty_position = True
#         strategy_excuted = None
#         while self.optionset.has_next():
#             # if self.underlying.eval_date == datetime.date(2016,11,23):
#             #     print('')
#             # if self.underlying.eval_date == datetime.date(2016,12,13):
#             #     print('')
#             self.update_arbitrage_window()
#             if empty_position:
#                 reverse, conversion = self.prepare_strategy()
#                 empty_position = not self.open_reverse(reverse)
#                 strategy_excuted = reverse
#             else:
#                 empty_position = self.close_signal(strategy_excuted,cd_strategy)
#             if isinstance(self.underlying,BaseFutureCoutinuous):
#                 self.underlying.shift_contract_month(self.account,self.slippage)
#             self.account.daily_accounting(self.optionset.eval_date)
#             self.optionset.next()
#             self.underlying.next()
#             print(self.base_index.eval_date,self.optionset.eval_date,self.underlying.eval_date)
#         return self.account
#
#     def back_test_c(self):
#         cd_strategy = 'conversion'
#         empty_position = True
#         strategy_excuted = None
#         while self.optionset.has_next():
#             # if self.underlying.eval_date == datetime.date(2016,11,23):
#             #     print('')
#             # if self.underlying.eval_date == datetime.date(2016,12,13):
#             #     print('')
#             self.update_arbitrage_window()
#             if empty_position:
#                 reverse, conversion = self.prepare_strategy()
#                 empty_position = not self.open_conversion(conversion)
#                 strategy_excuted = conversion
#             else:
#                 empty_position = self.close_signal(strategy_excuted,cd_strategy)
#             if isinstance(self.underlying,BaseFutureCoutinuous):
#                 self.underlying.shift_contract_month(self.account,self.slippage)
#             self.account.daily_accounting(self.optionset.eval_date)
#             self.optionset.next()
#             self.underlying.next()
#         return self.account
#
#     def back_test_b(self):
#         cd_strategy = 'box'# Box
#         empty_position = True
#         box = None
#         while self.optionset.has_next():
#             self.update_arbitrage_window()
#             if empty_position:
#                 box = self.prepare_box()
#                 # print(self.optionset.eval_date,box)
#                 empty_position = not self.open_box(box)
#             else:
#                 empty_position = self.close_signal(box,cd_strategy)
#             if isinstance(self.underlying,BaseFutureCoutinuous):
#                 self.underlying.shift_contract_month(self.account,self.slippage)
#             self.account.daily_accounting(self.optionset.eval_date)
#             self.optionset.next()
#             self.underlying.next()
#
#         return self.account





# start_date = datetime.date(2015, 2, 9)

"""
ETF Option Parity Arbitrage
"""

class ParityArbitrage(object):
    def __init__(self, df_option, df_underlying, df_future_c1=None, df_future_all=None,df_index=None):
        self.underlying = BaseInstrument(df_underlying)
        self.underlying.init()
        # self.underlying_unit_ratio = 1
        # self.underlying_m = 0.75
        self.future = None
        self.baseindex = None
        if df_future_c1 is not None:
            self.future = BaseFutureCoutinuous(df_future_c1=df_future_c1, df_futures_all_daily=df_future_all)
            self.future.init()
            self.future_unit_ratio = 1/1000.0
            # self.future_m = 1
        if df_index is not None:
            self.baseindex = BaseInstrument(df_index)
            self.baseindex.init()
        self.optionset = BaseOptionSet(df_option)
        self.optionset.init()
        self.rf = 0.03
        self.account = BaseAccount(c.Util.BILLION / 10,rf=self.rf)
        self.unit = 50
        self.min_holding = 1
        self.nbr_maturity = 0
        self.rank = 3
        self.slippage = 0
        self.aggregate_costs = 0.5/100.0
        self.cd_price = c.CdTradePrice.CLOSE
        self.df_arbitrage_window = pd.DataFrame()


    def update_sythetics(self):
        dt_maturity = self.optionset.select_maturity_date(nbr_maturity=self.nbr_maturity, min_holding=self.min_holding)
        self.t_quote = self.optionset.get_T_quotes(dt_maturity, self.cd_price)
        self.t_quote.loc[:, 'diff'] = abs(
            self.t_quote.loc[:, c.Util.AMT_APPLICABLE_STRIKE] - self.t_quote.loc[:, c.Util.AMT_UNDERLYING_CLOSE])
        self.t_quote.loc[:, 'rank'] = self.t_quote.index - self.t_quote['diff'].idxmin()
        discount = c.PricingUtil.get_discount(self.optionset.eval_date, dt_maturity, self.rf)
        self.t_quote.loc[:, 'sythetic_underlying'] = self.t_quote.loc[:, c.Util.AMT_CALL_QUOTE] \
                                                - self.t_quote.loc[:,c.Util.AMT_PUT_QUOTE] \
                                                + self.t_quote.loc[:,c.Util.AMT_APPLICABLE_STRIKE] * discount
        df_window = self.t_quote[(self.t_quote['rank']<=self.rank)&(self.t_quote['rank']>=-self.rank)] # 只考虑rank以内期权
        self.row_max_sythetic = df_window.loc[df_window['sythetic_underlying'].idxmax()]
        self.row_min_sythetic = df_window.loc[df_window['sythetic_underlying'].idxmin()]
        if self.future is not None:
            self.basis_to_etf = self.future.mktprice_close() - self.underlying.mktprice_close()*1000
            self.df_arbitrage_window.loc[self.optionset.eval_date, 'basis_to_etf'] = self.basis_to_etf
            self.df_arbitrage_window.loc[self.optionset.eval_date, 'ih'] = self.future.mktprice_close()
            if self.baseindex is not None:
                self.basis_to_index = self.future.mktprice_close() - self.baseindex.mktprice_close()
                self.tracking_error = self.underlying.mktprice_close()*1000 - self.baseindex.mktprice_close()
                self.df_arbitrage_window.loc[self.optionset.eval_date, 'basis_to_index'] = self.basis_to_index
                self.df_arbitrage_window.loc[self.optionset.eval_date, 'tracking_error'] = self.tracking_error
                self.df_arbitrage_window.loc[self.optionset.eval_date, 'index_50'] = self.baseindex.mktprice_close()
                # self.row_max_sythetic['tracking_error'] = self.tracking_error
                # self.row_min_sythetic['tracking_error'] = self.tracking_error
        self.df_arbitrage_window.loc[self.optionset.eval_date,'50etf'] = self.underlying.mktprice_close()
        self.df_arbitrage_window.loc[self.optionset.eval_date,'sythetic_underlying_max'] = self.row_max_sythetic['sythetic_underlying']
        self.df_arbitrage_window.loc[self.optionset.eval_date,'sythetic_underlying_min'] = self.row_min_sythetic['sythetic_underlying']

    def short_sythetic(self,df):
        # Short Sythetic
        self.conversion_call = self.optionset.get_baseoption_by_id(self.row_max_sythetic[c.Util.ID_CALL])
        fund_requirement = self.conversion_call.get_fund_required(c.LongShort.SHORT)
        df = df.append({'dt_date': self.optionset.eval_date,
                        'cd_posiiton': 'C_call',
                        'id_instrument': self.row_max_sythetic[c.Util.ID_CALL],
                        'base_instrument': self.conversion_call,
                        'long_short': c.LongShort.SHORT,
                        'fund_requirement': fund_requirement,
                        'cashflow_t0': self.conversion_call.mktprice_close() * self.conversion_call.multiplier(),
                        'unit_ratio' : 1},
                       ignore_index=True)
        self.conversion_put = self.optionset.get_baseoption_by_id(self.row_max_sythetic[c.Util.ID_PUT])
        fund_requirement = self.conversion_put.get_fund_required(c.LongShort.LONG)
        df = df.append({'dt_date': self.optionset.eval_date,
                        'cd_posiiton': 'C_put',
                        'id_instrument': self.row_max_sythetic[c.Util.ID_PUT],
                        'base_instrument': self.conversion_put,
                        'long_short': c.LongShort.LONG,
                        'fund_requirement': fund_requirement,
                        'cashflow_t0': -self.conversion_put.mktprice_close() * self.conversion_put.multiplier(),
                        'unit_ratio' : 1},
                       ignore_index=True)
        return df

    def long_sythetic(self,df):
        # Reverse : Long Sythetic
        self.reverse_call = self.optionset.get_baseoption_by_id(self.row_min_sythetic[c.Util.ID_CALL])
        fund_requirement = self.reverse_call.get_fund_required(c.LongShort.LONG)
        df = df.append({'dt_date': self.optionset.eval_date,
                        'cd_posiiton': 'R_call',
                        'id_instrument': self.row_min_sythetic[c.Util.ID_CALL],
                        'base_instrument': self.reverse_call,
                        'long_short': c.LongShort.LONG,
                        'fund_requirement': fund_requirement,
                        'cashflow_t0': -self.reverse_call.mktprice_close() * self.reverse_call.multiplier()},
                       ignore_index=True)
        self.reverse_put = self.optionset.get_baseoption_by_id(self.row_min_sythetic[c.Util.ID_PUT])
        fund_requirement = self.reverse_put.get_fund_required(c.LongShort.SHORT)
        df = df.append({'dt_date': self.optionset.eval_date,
                        'cd_posiiton': 'R_put',
                        'id_instrument': self.row_min_sythetic[c.Util.ID_PUT],
                        'base_instrument': self.reverse_put,
                        'long_short': c.LongShort.SHORT,
                        'fund_requirement': fund_requirement,
                        'cashflow_t0': self.reverse_put.mktprice_close() * self.reverse_put.multiplier()},
                       ignore_index=True)
        return df

    def long_etf(self,df):
        unit_ratio = self.conversion_put.multiplier()
        fund_requirement = self.conversion_put.multiplier() * self.underlying.mktprice_close()
        df = df.append({'dt_date': self.optionset.eval_date,
                        'cd_posiiton': 'underlying',
                        'id_instrument': self.underlying.id_instrument(),
                        'base_instrument': self.underlying,
                        'long_short': c.LongShort.LONG,
                        'fund_requirement': fund_requirement,
                        'cashflow_t0': -self.underlying.mktprice_close() * self.underlying.multiplier()*unit_ratio,
                        'unit_ratio' : unit_ratio},
                       ignore_index=True)
        return df

    def long_ih(self,df):
        unit_ratio = self.conversion_put.multiplier()/self.future.multiplier()/1000.0
        fund_requirement = self.future.mktprice_close()*self.future.multiplier()*unit_ratio
        df = df.append({'dt_date': self.optionset.eval_date,
                        'cd_posiiton': 'underlying',
                        'id_instrument': self.future.id_instrument(),
                        'base_instrument': self.future,
                        'long_short': c.LongShort.LONG,
                        'fund_requirement': fund_requirement,
                        'cashflow_t0': -self.future.mktprice_close() * self.future.multiplier()*unit_ratio,
                        'unit_ratio' : unit_ratio},
                       ignore_index=True)
        return df

    def short_ih(self,df):
        unit_ratio = self.reverse_put.multiplier()/self.future.multiplier()/1000.0
        fund_requirement = self.future.mktprice_close()*self.future.multiplier()*unit_ratio
        df = df.append({'dt_date': self.optionset.eval_date,
                        'cd_posiiton': 'underlying',
                        'id_instrument': self.future.id_instrument(),
                        'base_instrument': self.future,
                        'long_short': c.LongShort.SHORT,
                        'fund_requirement': fund_requirement,
                        'cashflow_t0': -self.future.mktprice_close() * self.future.multiplier()*unit_ratio,
                        'unit_ratio' : unit_ratio},
                       ignore_index=True)
        return df



    def open_signal(self,cd_strategy):
        if cd_strategy == 'box':
            if (self.row_max_sythetic['sythetic_underlying'] - self.row_min_sythetic['sythetic_underlying'])/self.underlying.mktprice_close() > self.aggregate_costs:
                df = pd.DataFrame(columns=['dt_date','id_instrument','base_instrument','long_short'])
                df = self.short_sythetic(df)
                df = self.long_sythetic(df)
                return df
            else:
                return None
        elif cd_strategy == 'conversion': # Converion : Short Sythetic, Long ETF
            if (self.row_max_sythetic['sythetic_underlying'] - self.underlying.mktprice_close())/self.underlying.mktprice_close() > self.aggregate_costs:
                df = pd.DataFrame(columns=['dt_date','id_instrument','base_instrument','long_short'])
                df = self.short_sythetic(df)
                df = self.long_etf(df)
                return df
            else:
                return None
        elif cd_strategy == 'conversion_ih': # Converion : Short Sythetic, Long IH # 主要布局IH负基差套利
            if self.optionset.eval_date.month ==5: return None #5月由于股票集中现金分红不做空Synthetic
            if (self.row_max_sythetic['sythetic_underlying']*1000.0 - self.future.mktprice_close()-
                    self.df_arbitrage_window.loc[self.optionset.eval_date,'tracking_error'])/self.future.mktprice_close() > self.aggregate_costs:
                df = pd.DataFrame(columns=['dt_date', 'id_instrument', 'base_instrument', 'long_short'])
                df = self.short_sythetic(df)
                df = self.long_ih(df)
                return df
            else:
                return None
        elif cd_strategy == 'ih_basis_arbitrage':
            # if self.df_arbitrage_window.loc[self.optionset.eval_date, 'basis_to_index'] > self.aggregate_costs: # 期货升水
            #     df = pd.DataFrame(columns=['dt_date', 'id_instrument', 'base_instrument', 'long_short'])
            #     df = self.short_ih(df)
            #     df = self.long_sythetic(df)
            #     return df
            if self.df_arbitrage_window.loc[self.optionset.eval_date, 'basis_to_index'] < -self.aggregate_costs:  # 期货贴水
                df = pd.DataFrame(columns=['dt_date', 'id_instrument', 'base_instrument', 'long_short'])
                df = self.short_sythetic(df)
                df = self.long_ih(df)
                return df
            else:
                return None
        elif cd_strategy == 'may_effect': # Reverse: Long Sythetic, Short IH # 5-9月分红期
            if self.optionset.eval_date.month ==5: #5月由于股票集中现金分红不做空Synthetic
                df = pd.DataFrame(columns=['dt_date', 'id_instrument', 'base_instrument', 'long_short'])
                df = self.long_sythetic(df)
                df = self.short_ih(df)
                return df
            else:
                return None


    def close_signal(self,cd_strategy,df_position):
        if cd_strategy == 'box':
            if self.reverse_call.maturitydt() == self.optionset.eval_date or self.conversion_call.maturitydt() == self.optionset.eval_date :
                return True
            # C_call = df_position[df_position['cd_position']=='C_call']['base_instrument'].values[0]
            # C_put = df_position[df_position['cd_position']=='C_put']['base_instrument'].values[0]
            # R_call = df_position[df_position['cd_position']=='R_call']['base_instrument'].values[0]
            # R_put = df_position[df_position['cd_position']=='R_put']['base_instrument'].values[0]
            discount_r = c.PricingUtil.get_discount(self.optionset.eval_date, self.reverse_put.maturitydt(), self.rf)
            discount_c = c.PricingUtil.get_discount(self.optionset.eval_date, self.conversion_put.maturitydt(), self.rf)
            reverse_sythetic = self.reverse_call.mktprice_close()-self.reverse_put.mktprice_close()+self.reverse_put.applicable_strike()*discount_r # Longed
            conversion_sythetic = self.conversion_call.mktprice_close()-self.conversion_put.mktprice_close()+self.conversion_put.applicable_strike()*discount_c # shorted
            if conversion_sythetic <= reverse_sythetic:
                return True
            else:
                return False
        elif cd_strategy == 'conversion_ih': # Short Sythetic, Long IH # 主要布局IH负基差套利
            if self.conversion_call.maturitydt() == self.optionset.eval_date:
                return True
            discount_c = c.PricingUtil.get_discount(self.optionset.eval_date, self.conversion_put.maturitydt(), self.rf)
            conversion_sythetic = self.conversion_call.mktprice_close() - self.conversion_put.mktprice_close() + self.conversion_put.applicable_strike() * discount_c  # shorted
            if conversion_sythetic*1000.0 <= self.future.mktprice_close():
                return True
            else:
                return False
        elif cd_strategy == 'ih_basis_arbitrage':
            if self.df_arbitrage_window.loc[self.optionset.eval_date, 'basis_to_index'] >= 0:
                return True
            else:
                return False
        elif cd_strategy == 'may_effect': # Reverse: Long Sythetic, Short IH # 5-9月分红期
            if self.optionset.eval_date.month !=5: #5月由于股票集中现金分红不做空Synthetic
                return True
            else:
                return False

    def open_excute(self,open_signal):
        if open_signal is None:
            return False
        else:
            fund_per_unit = open_signal['fund_requirement'].sum()
            unit = np.floor(self.account.cash*0.9/fund_per_unit) # TODO
            for (idx,row) in open_signal.iterrows():
                option = row['base_instrument']
                order = self.account.create_trade_order(option, row['long_short'], unit*row['unit_ratio'],
                                                        cd_trade_price=self.cd_price)
                record = option.execute_order(order, slippage=self.slippage)
                self.account.add_record(record, option)
            print(self.optionset.eval_date, ' open position')
            return True


    def close_excute(self):
        self.close_out()
        print(self.optionset.eval_date, ' close position')
        return True
        # else:
        #     for (idx,row) in close_signal.iterrows():
        #         option = row['base_instrument']
        #         order = self.account.create_trade_order(option, row['long_short'], row['unit'],
        #                                                 cd_trade_price=self.cd_price)
        #         record = option.execute_order(order, slippage=self.slippage)
        #         self.account.add_record(record, option)
        #     return True

    def close_out(self):
        close_out_orders = self.account.creat_close_out_order(cd_trade_price=c.CdTradePrice.CLOSE)
        for order in close_out_orders:
            execution_record = self.account.dict_holding[order.id_instrument] \
                .execute_order(order, slippage=self.slippage, execute_type=c.ExecuteType.EXECUTE_ALL_UNITS)
            self.account.add_record(execution_record, self.account.dict_holding[order.id_instrument])


    def back_test(self, cd_strategy):
        # TODO: 50ETF DIVIDEND
        empty_position = True
        df_position = None
        while self.optionset.has_next():
            if self.optionset.eval_date == datetime.date(2015,6,19):
                print('')
            self.update_sythetics()
            if empty_position:
                df_position = self.open_signal(cd_strategy)
                empty_position = not self.open_excute(df_position)
            elif self.close_signal(cd_strategy,df_position):
                empty_position = self.close_excute()
            if isinstance(self.underlying,BaseFutureCoutinuous):
                self.underlying.shift_contract_month(self.account,self.slippage)
            self.account.daily_accounting(self.optionset.eval_date)
            self.optionset.next()
            self.underlying.next()
            if self.future is not None: self.future.next()
            if self.baseindex is not None: self.baseindex.next()
        return self.account


start_date = datetime.date(2015, 5, 1)
# end_date = datetime.date.today()
end_date = datetime.date(2016,1,1)
# df_metrics = get_data.get_50option_mktdata(start_date, end_date)
# df_index = get_data.get_index_mktdata(start_date,end_date,c.Util.STR_INDEX_50ETF)
# df_f_c1 = get_data.get_mktdata_future_c1_daily(start_date,end_date,c.Util.STR_IH)
# df_f_all = get_data.get_future_mktdata(start_date,end_date,c.Util.STR_IH)
# df_sh50 = get_data.get_index_mktdata(start_date,end_date,c.Util.STR_INDEX_50SH)

df_sh50=pd.read_excel('../../data/df_sh50.xlsx')
df_metrics=pd.read_excel('../../data/df_metrics.xlsx')
df_index= pd.read_excel('../../data/df_index.xlsx')
df_f_c1=pd.read_excel('../../data/df_f_c1.xlsx')
df_f_all=pd.read_excel('../../data/df_f_all.xlsx')

df_metrics = df_metrics[df_metrics[c.Util.DT_DATE]>=start_date].reset_index(drop=True)
df_index = df_index[df_index[c.Util.DT_DATE]>=start_date].reset_index(drop=True)
df_f_c1 = df_f_c1[df_f_c1[c.Util.DT_DATE]>=start_date].reset_index(drop=True)
df_f_all = df_f_all[df_f_all[c.Util.DT_DATE]>=start_date].reset_index(drop=True)
df_sh50 = df_sh50[df_sh50[c.Util.DT_DATE]>=start_date].reset_index(drop=True)

df_metrics[c.Util.DT_DATE] = df_metrics[c.Util.DT_DATE].apply(lambda x: x.date())
df_index[c.Util.DT_DATE] = df_index[c.Util.DT_DATE].apply(lambda x: x.date())
df_f_c1[c.Util.DT_DATE] = df_f_c1[c.Util.DT_DATE].apply(lambda x: x.date())
df_f_all[c.Util.DT_DATE] = df_f_all[c.Util.DT_DATE].apply(lambda x: x.date())
df_sh50[c.Util.DT_DATE] = df_sh50[c.Util.DT_DATE].apply(lambda x: x.date())

df_metrics[c.Util.DT_MATURITY] = df_metrics[c.Util.DT_MATURITY].apply(lambda x: x.date())
df_f_all[c.Util.DT_MATURITY] = df_f_all[c.Util.DT_MATURITY].apply(lambda x: x.date())
parity = ParityArbitrage(df_metrics,df_index,df_future_c1=df_f_c1,df_future_all=df_f_all,df_index=df_sh50)
# parity = ParityArbitrage(df_metrics,df_index)

account = parity.back_test('conversion_ih')
# account = parity.back_test('ih_basis_arbitrage')
# account = parity.back_test('may_effect')

# parity.df_arbitrage_window.to_csv('../../accounts_data/ParityArbitrage-window.csv')
# account.account.to_csv('../../accounts_data/ParityArbitrage-account.csv')
# account.trade_records.to_csv('../../accounts_data/ParityArbitrage-records.csv')
print(account.trade_records)
res = account.analysis()
print(res)
pu = PlotUtil()
dates = list(account.account.index)
npv = list(account.account[c.Util.PORTFOLIO_NPV])
pu.plot_line_chart(dates, [npv], ['npv'])
plt.show()