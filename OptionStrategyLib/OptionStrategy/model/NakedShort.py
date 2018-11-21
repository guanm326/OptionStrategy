from back_test.model.base_option_set import BaseOptionSet
from back_test.model.base_account import BaseAccount
from back_test.model.base_option import BaseOption
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



class NakedShort(object):

    def __init__(self,start_date,end_date):

        self.start_date = start_date
        self.end_date = end_date
        df_metrics = get_data.get_50option_mktdata(start_date, end_date)

        self.min_holding = 20
        self.init_fund = c.Util.BILLION
        self.slippage = 0
        self.m = 1  # 期权notional倍数
        self.moneyness_rank = -3
        self.nbr_maturity = 0
        self.cd_trade_price = c.CdTradePrice.VOLUME_WEIGHTED
        self.account = BaseAccount(init_fund=c.Util.BILLION, leverage=1.0, rf=0.03)
        self.optionset = BaseOptionSet(df_metrics)
        self.optionset.init()

    # def stop_loss(call, put):
    #     spot = call.underlying_last_close()
    #     if spot is None:
    #         return False
    #     if call.strike() < spot or put.strike() > spot:
    #         print(call.eval_date,' stop loss')
    #         return True
    #     else:
    #         return False

    def close_position(self):
        # stop_loss(call,put)
        dt_maturity = None
        for option in self.account.dict_holding.values():
            if isinstance(option, BaseOption) and option is not None:
                dt_maturity = option.maturitydt()
                break
        if (dt_maturity - self.optionset.eval_date).days <= 5:
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

        while self.optionset.eval_date <= self.end_date:

            # print(optionset.eval_date)
            # if self.account.cash <= 0: break
            if self.optionset.eval_date >= self.end_date:  # Final close out all.
                self.close_out()
                self.account.daily_accounting(self.optionset.eval_date)
                print(self.optionset.eval_date,
                      self.account.account.loc[self.optionset.eval_date, c.Util.PORTFOLIO_NPV])
                break

            # 平仓
            if not empty_position and self.close_position():
                self.close_all_options()
                empty_position = True

            # 开仓
            if empty_position:
                empty_position = self.excute(self.short_straddle())

            self.account.daily_accounting(self.optionset.eval_date)
            print(self.optionset.eval_date,self.account.account.loc[self.optionset.eval_date,c.Util.PORTFOLIO_NPV])
            if not self.optionset.has_next(): break
            self.optionset.next()




""" example """

naked_short = NakedShort(datetime.date(2015,1,1),datetime.date(2018,10,8))
naked_short.back_test()

naked_short.account.account.to_csv('../../accounts_data/naked_short_account_' + str(naked_short.moneyness_rank) + '.csv')
naked_short.account.trade_records.to_csv('../../accounts_data/naked_short_records_' + str(naked_short.moneyness_rank) + '.csv')
res = naked_short.account.analysis()
print(res)

dates = list(naked_short.account.account.index)
npv = list(naked_short.account.account[c.Util.PORTFOLIO_NPV])
pu = PlotUtil()
pu.plot_line_chart(dates, [npv], ['npv'])
plt.show()
