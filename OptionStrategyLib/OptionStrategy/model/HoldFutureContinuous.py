from back_test.model.base_option_set import BaseOptionSet
from back_test.model.base_option import BaseOption
from back_test.model.base_account import BaseAccount
from back_test.model.base_instrument import BaseInstrument
from back_test.model.base_future_coutinuous import BaseFutureCoutinuous
import data_access.get_data as get_data
import back_test.model.constant as c
import datetime
import numpy as np

import pandas as pd
from OptionStrategyLib.VolatilityModel.historical_volatility import HistoricalVolatilityModels as histvol


class HoldFutureContinuous(object):
    def __init__(self,df_c1,df_all,df_baseindex):
        self.slippage = 0
        self.cd_trade_price = c.CdTradePrice.VOLUME_WEIGHTED
        dt_start = max(df_baseindex[c.Util.DT_DATE].values[0], df_c1[c.Util.DT_DATE].values[0])
        self.end_date = min(df_baseindex[c.Util.DT_DATE].values[-1], df_c1[c.Util.DT_DATE].values[-1])
        df_baseindex = df_baseindex[df_baseindex[c.Util.DT_DATE] >= dt_start].reset_index(drop=True)
        df_c1 = df_c1[df_c1[c.Util.DT_DATE] >= dt_start].reset_index(drop=True)
        df_all = df_all[df_all[c.Util.DT_DATE] >= dt_start].reset_index(drop=True)
        self.invst_portfolio = BaseFutureCoutinuous(df_c1,df_futures_all_daily=df_all)  # e.g., top 50 low volatility index
        self.invst_portfolio.init()
        self.index = BaseInstrument(df_baseindex)
        self.index.init()
        self.account = BaseAccount(init_fund=c.Util.BILLION, leverage=1.0, rf=0.03)


    def close_all_options(self):
        for option in self.account.dict_holding.values():
            if isinstance(option, BaseOption):
                order = self.account.create_close_order(option, cd_trade_price=self.cd_trade_price)
                record = option.execute_order(order, slippage=self.slippage)
                self.account.add_record(record, option)
        self.dict_strategy = {}

    def close_out(self):
        close_out_orders = self.account.creat_close_out_order(cd_trade_price=c.CdTradePrice.CLOSE)
        for order in close_out_orders:
            execution_record = self.account.dict_holding[order.id_instrument] \
                .execute_order(order, slippage=self.slippage, execute_type=c.ExecuteType.EXECUTE_ALL_UNITS)
            self.account.add_record(execution_record, self.account.dict_holding[order.id_instrument])

    def back_test(self):
        self.unit_index = np.floor(self.account.cash / self.index.mktprice_close() / self.index.multiplier())

        unit_portfolio = np.floor(self.account.cash / self.invst_portfolio.mktprice_close() / self.invst_portfolio.multiplier())
        order_index = self.account.create_trade_order(self.invst_portfolio, c.LongShort.LONG, unit_portfolio,
                                                          cd_trade_price=c.CdTradePrice.CLOSE)
        record_index = self.invst_portfolio.execute_order(order_index, slippage=self.slippage)
        self.account.add_record(record_index, self.invst_portfolio)
        init_index = self.index.mktprice_close()
        index_npv = []
        while self.invst_portfolio.eval_date <= self.end_date:
            if self.invst_portfolio.eval_date >= self.end_date:  # Final close out all.
                close_out_orders = self.account.creat_close_out_order()
                for order in close_out_orders:
                    execution_record = self.account.dict_holding[order.id_instrument] \
                        .execute_order(order, slippage=self.slippage, execute_type=c.ExecuteType.EXECUTE_ALL_UNITS)
                    self.account.add_record(execution_record, self.account.dict_holding[order.id_instrument])
                self.account.daily_accounting(self.invst_portfolio.eval_date)
                index_npv.append(self.index.mktprice_close() / init_index)
                print(self.invst_portfolio.eval_date, ' close out ')
                break

            #移仓换月
            self.invst_portfolio.shift_contract_month(self.account,self.slippage)

            self.account.daily_accounting(self.invst_portfolio.eval_date)
            index_npv.append(self.index.mktprice_close() / init_index)
            if not self.invst_portfolio.has_next(): break
            self.invst_portfolio.next()
            self.index.next()
        self.account.account['baseindex_npv'] = index_npv
        return self.account
