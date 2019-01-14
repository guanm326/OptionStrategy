import datetime
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import back_test.model.constant as c
from Utilities.PlotUtil import PlotUtil
from back_test.model.base_account import BaseAccount
from back_test.model.base_future_coutinuous import BaseFutureCoutinuous
from back_test.model.base_future_set import BaseFutureSet
from back_test.model.base_instrument import BaseInstrument
from back_test.model.base_option_set import BaseOptionSet


"""
Put Call Parity Arbitrage
for ETF Option & Commodity Option
use futureset instead of futurecontinuous
"""

class ParityArbitrage(object):
    def __init__(self,name_code, df_option, df_etf=None, df_future_all=None,df_index=None):
        self.name_code = name_code
        self.df_option = df_option
        self.df_etf = df_etf
        self.df_future_all = df_future_all
        self.df_index = df_index
        self.rf = 0.03
        self.m = 0.9
        self.account = BaseAccount(c.Util.BILLION / 10,rf=self.rf)
        self.unit = 50
        self.min_holding = 6 # 50ETF与IH到期日相差5天
        self.nbr_maturity = 0
        self.rank = 3
        self.slippage = 0
        self.aggregate_costs = 0.5/100.0
        self.cd_price = c.CdTradePrice.CLOSE
        self.df_arbitrage_window = pd.DataFrame()

    def init(self):
        self.underlying = None
        self.futureset = None
        self.baseindex = None
        self.optionset = BaseOptionSet(self.df_option)
        self.optionset.init()
        if self.name_code == c.Util.STR_50ETF:
            if self.df_etf is not None:
                self.underlying = BaseInstrument(self.df_etf) # 50ETF
                self.underlying.init()
            if self.df_future_all is not None:
                self.futureset = BaseFutureSet(self.df_future_all) # IH
                self.futureset.init()
                self.future_unit_ratio = 1/1000.0
            if self.df_index is not None:
                self.baseindex = BaseInstrument(self.df_index) # SH50
                self.baseindex.init()
        else: # 商品期权
            if self.df_future_all is not None:
                self.futureset = BaseFutureSet(self.df_future_all) # IH
                self.futureset.init()
                self.future_unit_ratio = 1.0
            # self.optionset = BaseOptionSet(self.df_option)
            # self.optionset.init()

    def update_sythetics(self):
        if self.name_code == c.Util.STR_50ETF:
            dt_maturity = self.optionset.select_maturity_date(nbr_maturity=self.nbr_maturity, min_holding=self.min_holding)
            contract_month = self.optionset.get_dict_options_by_maturities()[dt_maturity][0].contract_month()

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
            self.df_arbitrage_window.loc[self.optionset.eval_date,'50etf'] = self.underlying.mktprice_close()
            self.df_arbitrage_window.loc[self.optionset.eval_date,'sythetic_underlying_max'] = self.row_max_sythetic['sythetic_underlying']
            self.df_arbitrage_window.loc[self.optionset.eval_date,'sythetic_underlying_min'] = self.row_min_sythetic['sythetic_underlying']
            if self.futureset is not None:
                future = self.futureset.select_future_by_contract_month(contract_month)
                self.row_max_sythetic['future'] = future
                if future is None:
                    return
                self.basis_to_etf = future.mktprice_close() - self.underlying.mktprice_close()/self.future_unit_ratio
                self.df_arbitrage_window.loc[self.optionset.eval_date, 'basis_to_etf'] = self.basis_to_etf
                self.df_arbitrage_window.loc[self.optionset.eval_date, 'ih'] = future.mktprice_close()
                if self.baseindex is not None:
                    self.basis_to_index = future.mktprice_close() - self.baseindex.mktprice_close()
                    self.tracking_error = self.underlying.mktprice_close()/self.future_unit_ratio - self.baseindex.mktprice_close()
                    self.df_arbitrage_window.loc[self.optionset.eval_date, 'basis_to_index'] = self.basis_to_index
                    self.df_arbitrage_window.loc[self.optionset.eval_date, 'tracking_error'] = self.tracking_error
                    self.df_arbitrage_window.loc[self.optionset.eval_date, 'index_50'] = self.baseindex.mktprice_close()
        else:
            dt_maturity = self.optionset.select_maturity_date(nbr_maturity=self.nbr_maturity, min_holding=self.min_holding)
            contract_month = self.optionset.get_dict_options_by_maturities()[dt_maturity][0].contract_month()
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
            future = self.futureset.select_future_by_contract_month(contract_month)
            self.underlying = future
            self.df_arbitrage_window.loc[self.optionset.eval_date, 'underlying'] = self.underlying.mktprice_close()
            self.df_arbitrage_window.loc[self.optionset.eval_date, 'sythetic_underlying_max'] = self.row_max_sythetic[
                'sythetic_underlying']
            self.df_arbitrage_window.loc[self.optionset.eval_date, 'sythetic_underlying_min'] = self.row_min_sythetic[
                'sythetic_underlying']


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
            future = self.row_max_sythetic['future']
            if future is None: return None
            self.future = future
            if (self.row_max_sythetic['sythetic_underlying']/self.future_unit_ratio - future.mktprice_close()-
                    self.df_arbitrage_window.loc[self.optionset.eval_date,'tracking_error'])/future.mktprice_close() > self.aggregate_costs:
                df = pd.DataFrame(columns=['dt_date', 'id_instrument', 'base_instrument', 'long_short'])
                df = self.short_sythetic(df)
                df = self.long_ih(df,future)
                return df
            else:
                return None
        elif cd_strategy == 'ih_basis_arbitrage':
            future = self.row_max_sythetic['future']
            if future is None: return None
            self.future = future
            if self.df_arbitrage_window.loc[self.optionset.eval_date, 'basis_to_index'] < -self.aggregate_costs:  # 期货贴水
                df = pd.DataFrame(columns=['dt_date', 'id_instrument', 'base_instrument', 'long_short'])
                df = self.short_sythetic(df)
                df = self.long_ih(df,future)
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
            discount_r = c.PricingUtil.get_discount(self.optionset.eval_date, self.reverse_put.maturitydt(), self.rf)
            discount_c = c.PricingUtil.get_discount(self.optionset.eval_date, self.conversion_put.maturitydt(), self.rf)
            reverse_sythetic = self.reverse_call.mktprice_close()-self.reverse_put.mktprice_close()+self.reverse_put.applicable_strike()*discount_r # Longed
            conversion_sythetic = self.conversion_call.mktprice_close()-self.conversion_put.mktprice_close()+self.conversion_put.applicable_strike()*discount_c # shorted
            if conversion_sythetic <= reverse_sythetic:
                return True
            else:
                return False
        elif cd_strategy == 'conversion': # Short Sythetic, Long Underlying # 主要布局IH负基差套利
            if self.conversion_call.maturitydt() == self.optionset.eval_date:
                return True
            discount_c = c.PricingUtil.get_discount(self.optionset.eval_date, self.conversion_put.maturitydt(), self.rf)
            conversion_sythetic = self.conversion_call.mktprice_close() - self.conversion_put.mktprice_close() + self.conversion_put.applicable_strike() * discount_c  # shorted
            if conversion_sythetic/self.future_unit_ratio <= self.underlying.mktprice_close():
                return True
            else:
                return False
        elif cd_strategy == 'conversion_ih': # Short Sythetic, Long IH # 主要布局IH负基差套利
            if self.conversion_call.maturitydt() == self.optionset.eval_date or self.future.maturitydt() == self.optionset.eval_date:
                return True
            discount_c = c.PricingUtil.get_discount(self.optionset.eval_date, self.conversion_put.maturitydt(), self.rf)
            conversion_sythetic = self.conversion_call.mktprice_close() - self.conversion_put.mktprice_close() + self.conversion_put.applicable_strike() * discount_c  # shorted
            if conversion_sythetic/self.future_unit_ratio <= self.future.mktprice_close():
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
            unit = np.floor(self.account.cash*self.m/fund_per_unit)
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

    def long_ih(self,df,future):
        unit_ratio = self.conversion_put.multiplier()/future.multiplier()/1000.0
        fund_requirement = future.mktprice_close()*future.multiplier()*unit_ratio
        df = df.append({'dt_date': self.optionset.eval_date,
                        'cd_posiiton': 'underlying',
                        'id_instrument': future.id_instrument(),
                        'base_instrument': future,
                        'long_short': c.LongShort.LONG,
                        'fund_requirement': fund_requirement,
                        'cashflow_t0': -future.mktprice_close() * future.multiplier()*unit_ratio,
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


    def back_test(self, cd_strategy):
        # TODO: DIVIDEND
        empty_position = True
        df_position = None
        while self.optionset.has_next():
            # if self.optionset.eval_date == datetime.date(2015,5,18):
            #     print('')
            self.update_sythetics()
            if empty_position:
                df_position = self.open_signal(cd_strategy)
                empty_position = not self.open_excute(df_position)
            elif self.close_signal(cd_strategy,df_position):
                empty_position = self.close_excute()
            # if isinstance(self.underlying,BaseFutureCoutinuous):
            #     self.underlying.shift_contract_month(self.account,self.slippage)
            self.account.daily_accounting(self.optionset.eval_date)
            self.optionset.next()
            self.underlying.next()
            if self.futureset is not None: self.futureset.next()
            if self.baseindex is not None: self.baseindex.next()
            # print(self.optionset.eval_date)
        return self.account

    def back_test_comdty(self, cd_strategy):
        # TODO: DIVIDEND
        empty_position = True
        df_position = None
        while self.optionset.has_next():
            # if self.optionset.eval_date == datetime.date(2015,5,18):
            #     print('')
            self.update_sythetics()
            if empty_position:
                df_position = self.open_signal(cd_strategy)
                empty_position = not self.open_excute(df_position)
            elif self.close_signal(cd_strategy,df_position):
                empty_position = self.close_excute()
            # if isinstance(self.underlying,BaseFutureCoutinuous):
            #     self.underlying.shift_contract_month(self.account,self.slippage)
            self.account.daily_accounting(self.optionset.eval_date)
            self.optionset.next()
            self.futureset.next()
            # if self.baseindex is not None: self.baseindex.next()
            # print(self.optionset.eval_date)
        return self.account

