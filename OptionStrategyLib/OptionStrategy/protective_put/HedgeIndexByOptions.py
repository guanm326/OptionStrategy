from back_test.model.base_option_set import BaseOptionSet
from back_test.model.base_option import BaseOption
from back_test.model.base_account import BaseAccount
from back_test.model.base_instrument import BaseInstrument
import data_access.get_data as get_data
import back_test.model.constant as c
import datetime
import numpy as np
from Utilities.PlotUtil import PlotUtil
import matplotlib.pyplot as plt
import pandas as pd
from OptionStrategyLib.VolatilityModel.historical_volatility import HistoricalVolatilityModels as histvol


class HedgeIndexByOptions(object):
    def __init__(self, df_baseindex, df_option_metrics,
                 cd_direction_timing='ma_5_60',
                 cd_strategy='bull_spread', cd_volatility='close_std'):
        self.min_holding = 20
        self.slippage = 0
        self.nbr_maturity = 0
        self.cd_trade_price = c.CdTradePrice.VOLUME_WEIGHTED
        dt_start = max(df_option_metrics[c.Util.DT_DATE].values[0], df_baseindex[c.Util.DT_DATE].values[0])
        df_metrics = df_option_metrics[df_option_metrics[c.Util.DT_DATE] >= dt_start].reset_index(drop=True)
        df_index = df_baseindex[df_baseindex[c.Util.DT_DATE] >= dt_start].reset_index(drop=True)
        self.optionset = BaseOptionSet(df_metrics)
        self.index = BaseInstrument(df_index)
        self.optionset.init()
        self.index.init()
        self.account = BaseAccount(init_fund=c.Util.BILLION, leverage=1.0, rf=0.03)
        self.prepare_timing(df_baseindex)
        self.cd_direction_timing = cd_direction_timing
        # self.cd_strike_spread = cd_strike_spread
        self.cd_strategy = cd_strategy
        self.cd_volatility = cd_volatility
        self.cd_short_ma = 'ma_5'
        self.cd_long_ma = 'ma_60'
        self.cd_std = 'std_10'
        self.unit_index = None
        self.dict_strategy = {}

    def prepare_timing(self, df_index):
        df_index['ma_5'] = c.Statistics.moving_average(df_index[c.Util.AMT_CLOSE], n=5).shift()
        df_index['ma_60'] = c.Statistics.moving_average(df_index[c.Util.AMT_CLOSE], n=60).shift()
        df_index['ma_120'] = c.Statistics.moving_average(df_index[c.Util.AMT_CLOSE], n=120).shift()
        df_index['std_5'] = c.Statistics.standard_deviation(df_index[c.Util.AMT_CLOSE], n=5).shift()
        df_index['std_10'] = c.Statistics.standard_deviation(df_index[c.Util.AMT_CLOSE], n=10).shift()
        df_index['std_15'] = c.Statistics.standard_deviation(df_index[c.Util.AMT_CLOSE], n=15).shift()
        df_index['std_20'] = c.Statistics.standard_deviation(df_index[c.Util.AMT_CLOSE], n=20).shift()
        df_index['histvol_5'] = histvol.hist_vol(df_index[c.Util.AMT_CLOSE], n=5).shift() / np.sqrt(252)
        df_index['histvol_10'] = histvol.hist_vol(df_index[c.Util.AMT_CLOSE], n=10).shift() / np.sqrt(252)
        df_index['histvol_20'] = histvol.hist_vol(df_index[c.Util.AMT_CLOSE], n=20).shift() / np.sqrt(252)
        df_index['histvol_30'] = histvol.hist_vol(df_index[c.Util.AMT_CLOSE], n=30).shift() / np.sqrt(252)
        df_index['histvol_60'] = histvol.hist_vol(df_index[c.Util.AMT_CLOSE], n=60).shift() / np.sqrt(252)
        df_index['histvol_90'] = histvol.hist_vol(df_index[c.Util.AMT_CLOSE], n=90).shift() / np.sqrt(252)
        # df_index = df_index.set_index(c.Util.DT_DATE)
        df_index.to_csv('../../accounts_data/df_index1.csv')
        self.df_timing = df_index.set_index(c.Util.DT_DATE)
        # return df_index

    def open_signal(self):
        if self.cd_direction_timing == 'ma_5_60':
            return self.open_position_ma()

    def close_signal(self):
        if self.cd_direction_timing == 'ma_5_60':
            return self.close_position_ma()

    def strategy(self):
        if self.cd_strategy == 'bull_spread':
            if self.cd_volatility == 'close_std':
                dt_date = self.optionset.eval_date
                std_close = self.df_timing.loc[dt_date, self.cd_std]
                k_short = self.index.mktprice_open() - std_close
                put_long, put_short = self.bull_spread(k_short)
                return {c.LongShort.SHORT:put_short, c.LongShort.LONG:put_long}

    def shift(self):
        if self.cd_strategy == 'bull_spread':
            return self.shift_bull_spread()

    def open_position_ma(self):
        dt_date = self.optionset.eval_date
        if dt_date not in self.df_timing.index:
            return False
        ma_5 = self.df_timing.loc[dt_date, self.cd_short_ma]
        ma_60 = self.df_timing.loc[dt_date, self.cd_long_ma]
        if ma_5 < ma_60:
            return True
        else:
            return False

    def close_position_ma(self):
        dt_date = self.optionset.eval_date
        dt_maturity = None
        for option in self.account.dict_holding.values():
            if isinstance(option, BaseOption):
                dt_maturity = option.maturitydt()
                break
        if (dt_maturity - dt_date).days <= 5:
            return True
        ma_5 = self.df_timing.loc[dt_date, self.cd_short_ma]
        ma_60 = self.df_timing.loc[dt_date, self.cd_long_ma]
        if ma_5 > ma_60:
            return True
        else:
            return False

    def bull_spread(self, k_short):
        maturity = self.optionset.select_maturity_date(nbr_maturity=self.nbr_maturity, min_holding=self.min_holding)
        xx, list_put0 = self.optionset.get_options_list_by_moneyness_mthd1(moneyness_rank=self.nbr_maturity,
                                                                           maturity=maturity,
                                                                           cd_price=c.CdPriceType.OPEN)
        put_long = self.optionset.select_higher_volume(list_put0)
        # if put_long is None:
        #     xxx, list_put0 = optionset.get_options_list_by_moneyness_mthd1(moneyness_rank=0,
        #                                                                   maturity=maturity,
        #                                                                   cd_price=c.CdPriceType.OPEN)
        #     put_long = optionset.select_higher_volume(list_put0)
        put_short = self.optionset.select_higher_volume(
            self.optionset.get_option_closest_strike(c.OptionType.PUT, k_short, maturity))
        if put_short.id_instrument() == put_long.id_instrument():
            put_short = None
        return put_long, put_short

    def shift_bull_spread(self):
        option_short = self.dict_strategy[c.LongShort.SHORT]
        option_long = self.dict_strategy[c.LongShort.LONG]
        if option_short is None:
            # return self.strategy()
            return None

        else:
            if self.index.mktprice_open() <= (option_long.strike() + option_short.strike()) / 2:
                return self.strategy()

            else:
                return None

    def excute(self,dict_strategy):
        if dict_strategy is None: return
        for long_short in dict_strategy.keys():
            option = dict_strategy[long_short]
            if option is None:
                continue
            elif long_short in self.dict_strategy.keys() and self.dict_strategy[long_short] is not None\
                    and option.id_instrument() == self.dict_strategy[long_short].id_instrument():
                continue
            unit = self.unit_index / option.multiplier()
            order = self.account.create_trade_order(option, long_short, unit, cd_trade_price=self.cd_trade_price)
            record = option.execute_order(order, slippage=self.slippage)
            self.account.add_record(record, option)
        self.dict_strategy = dict_strategy

    def close_all_options(self):
        for option in self.account.dict_holding.values():
            if isinstance(option, BaseOption):
                order = self.account.create_close_order(option, cd_trade_price=self.cd_trade_price)
                record = option.execute_order(order, slippage=self.slippage)
                self.account.add_record(record, option)
        self.dict_strategy = {}


    def back_test(self):
        self.unit_index = np.floor(self.account.cash / self.index.mktprice_close() / self.index.multiplier())

        order_index = self.account.create_trade_order(self.index, c.LongShort.LONG, self.unit_index,
                                                 cd_trade_price=c.CdTradePrice.CLOSE)
        record_index = self.index.execute_order(order_index, slippage=self.slippage)
        self.account.add_record(record_index, self.index)

        empty_position = True
        init_index = self.index.mktprice_close()
        base_npv = []
        maturity1 = self.optionset.select_maturity_date(nbr_maturity=self.nbr_maturity, min_holding=self.min_holding)
        end_date = datetime.date(2018,11,1)
        while self.optionset.eval_date <= end_date:
            print(self.optionset.eval_date)
            # if self.optionset.eval_date >= datetime.date(2016,1,25):
            #     print('')
            if maturity1 > end_date:  # Final close out all.
                close_out_orders = self.account.creat_close_out_order()
                for order in close_out_orders:
                    execution_record = self.account.dict_holding[order.id_instrument] \
                        .execute_order(order, slippage=self.slippage, execute_type=c.ExecuteType.EXECUTE_ALL_UNITS)
                    self.account.add_record(execution_record, self.account.dict_holding[order.id_instrument])
                self.account.daily_accounting(self.optionset.eval_date)
                base_npv.append(self.index.mktprice_close() / init_index)
                print(self.optionset.eval_date, ' close out ')
                break

            if not empty_position:
                if self.close_signal():
                    self.close_all_options()
                    empty_position = True
                else:
                    strategy = self.shift()
                    if strategy is not None:
                        self.close_all_options()
                        self.excute(strategy)
            else:
                if self.open_signal():
                    self.excute(self.strategy())
                    empty_position = False

            self.account.daily_accounting(self.optionset.eval_date)
            base_npv.append(self.index.mktprice_close() / init_index)
            if not self.optionset.has_next(): break
            self.optionset.next()
            self.index.next()

        res = self.account.analysis()
        print(res)
        self.account.account['base_npv'] = base_npv
        self.account.account.to_csv('../../accounts_data/hedge_by_option_account_' + self.cd_strategy + '.csv')
        self.account.trade_records.to_csv('../../accounts_data/hedge_by_option_records_' + self.cd_strategy + '.csv')
        pu = PlotUtil()
        dates = list(self.account.account.index)
        hedged_npv = list(self.account.account[c.Util.PORTFOLIO_NPV])
        pu.plot_line_chart(dates, [hedged_npv, base_npv], ['hedged_npv', 'base_npv'])
        plt.show()

# def bull_spread_vol_1(df_index, optionset):
#     name = 'bull_spread_vol'
#     dt_date = optionset.eval_date
#     maturity = optionset.select_maturity_date(nbr_maturity=self.nbr_maturity, min_holding=min_holding)
#     xx, list_put0 = optionset.get_options_list_by_moneyness_mthd1(moneyness_rank=0,
#                                                                   maturity=maturity,
#                                                                   cd_price=c.CdPriceType.OPEN)
#     put_long = optionset.select_higher_volume(list_put0)
#     # if put_long is None:
#     #     xxx, list_put0 = optionset.get_options_list_by_moneyness_mthd1(moneyness_rank=0,
#     #                                                                   maturity=maturity,
#     #                                                                   cd_price=c.CdPriceType.OPEN)
#     #     put_long = optionset.select_higher_volume(list_put0)
#     std_yield = df_index.loc[dt_date, 'histvol_10']
#     k_target = put_long.strike() * (1 - std_yield)
#     put_short = optionset.select_higher_volume(
#         optionset.get_option_closest_strike(c.OptionType.PUT, k_target, maturity))
#     # if put_short.strike() >= k_target:
#     #     put_short = None
#     return [put_long, put_short], name
# def collar(optionset):
#     name = 'collar'
#     maturity0 = optionset.select_maturity_date(nbr_maturity=0, min_holding=20)
#     maturity1 = optionset.select_maturity_date(nbr_maturity=1, min_holding=20)
#
#     list_call, xx = optionset.get_options_list_by_moneyness_mthd1(moneyness_rank=-2,
#                                                                   maturity=maturity0,
#                                                                   cd_price=c.CdPriceType.OPEN)
#     xxx, list_put = optionset.get_options_list_by_moneyness_mthd1(moneyness_rank=-2,
#                                                                   maturity=maturity1,
#                                                                   cd_price=c.CdPriceType.OPEN)
#     call = optionset.select_higher_volume(list_call)
#     put = optionset.select_higher_volume(list_put)
#     if put is None:
#         xxx, list_put = optionset.get_options_list_by_moneyness_mthd1(moneyness_rank=0,
#                                                                       maturity=maturity1,
#                                                                       cd_price=c.CdPriceType.OPEN)
#         put = optionset.select_higher_volume(list_put)
#     # res = {call: c.LongShort.SHORT, put: c.LongShort.LONG}
#     return [call, put], name
#
#
# def bull_spread(optionset):
#     name = 'bull_spread'
#     maturity = optionset.select_maturity_date(nbr_maturity=0, min_holding=min_holding)
#
#     xx, list_put0 = optionset.get_options_list_by_moneyness_mthd1(moneyness_rank=0,
#                                                                   maturity=maturity,
#                                                                   cd_price=c.CdPriceType.OPEN)
#     xxx, list_put2 = optionset.get_options_list_by_moneyness_mthd1(moneyness_rank=-2,
#                                                                    maturity=maturity,
#                                                                    cd_price=c.CdPriceType.OPEN)
#     put_long = optionset.select_higher_volume(list_put0)
#     put_short = optionset.select_higher_volume(list_put2)
#     # res = {put0: c.LongShort.LONG, put2: c.LongShort.SHORT}
#     return [put_long, put_short], name
#
#
# def three_way(df_index, optionset):
#     name = 'three_way'
#     dt_date = optionset.eval_date
#     maturity = optionset.select_maturity_date(nbr_maturity=0, min_holding=20)
#     xxx, list_put0 = optionset.get_options_list_by_moneyness_mthd1(moneyness_rank=0,
#                                                                    maturity=maturity,
#                                                                    cd_price=c.CdPriceType.OPEN)
#     put_long = optionset.select_higher_volume(list_put0)
#     std_close = df_index.loc[dt_date, 'std_close']
#     k_low = np.floor(put_long.strike() - std_close)
#     put_short = optionset.select_higher_volume(optionset.get_option_by_strike(c.OptionType.PUT, k_low, maturity))
#     k_high = np.floor(put_long.strike() + std_close)
#     call_short = optionset.select_higher_volume(optionset.get_option_by_strike(c.OptionType.CALL, k_high, maturity))
#     return [put_long, put_short, call_short], name
#
#
# def buy_put(optionset):
#     name = 'buy_put'
#     maturity = optionset.select_maturity_date(nbr_maturity=0, min_holding=min_holding)
#
#     xx, list_put0 = optionset.get_options_list_by_moneyness_mthd1(moneyness_rank=-2,
#                                                                   maturity=maturity,
#                                                                   cd_price=c.CdPriceType.OPEN)
#     put = optionset.select_higher_volume(list_put0)
#     if put is None:
#         xxx, list_put = optionset.get_options_list_by_moneyness_mthd1(moneyness_rank=0,
#                                                                       maturity=maturity,
#                                                                       cd_price=c.CdPriceType.OPEN)
#         put = optionset.select_higher_volume(list_put)
#     return [put], name
#
#
# def excute_delta(strategy_res, unit_index, account):
#     delta = 0
#     multiplier = None
#     for option in strategy_res.keys():
#         if option is None:
#             continue
#         delta += option.get_delta(option.get_implied_vol()) * strategy_res[option].value
#         multiplier = option.multiplier()
#     unit = unit_index / multiplier / abs(delta)
#     for option in strategy_res.keys():
#         if option is None:
#             continue
#         order = account.create_trade_order(option, strategy_res[option], unit, cd_trade_price=cd_trade_price)
#         record = option.execute_order(order, slippage=slippage)
#         account.add_record(record, option)
#
#
# def shift_bull_spread(option_long, option_short, spot, optionset):
#     if option_short is None:
#         maturity = optionset.select_maturity_date(nbr_maturity=0, min_holding=20)
#         xxx, list_put2 = optionset.get_options_list_by_moneyness_mthd1(moneyness_rank=-2,
#                                                                        maturity=maturity,
#                                                                        cd_price=c.CdPriceType.OPEN)
#         put2 = optionset.select_higher_volume(list_put2)
#         if put2 is None:
#             return False
#         else:
#             print(optionset.eval_date, ' shift')
#             return True
#     else:
#         if spot < option_long.strike():
#             print(optionset.eval_date, ' shift')
#             return True
#         else:
#             return False
#
#
# def shift_buy_put(put, spot):
#     if spot <= put.strike():
#         return True
#
#
# def shift_collar(call, put, spot, optionset):
#     k_call = call.strike()
#     k_put = put.strike()
#     if call is None:
#         maturity = optionset.select_maturity_date(nbr_maturity=0, min_holding=20)
#         list_call, xxx = optionset.get_options_list_by_moneyness_mthd1(moneyness_rank=-2,
#                                                                        maturity=maturity,
#                                                                        cd_price=c.CdPriceType.OPEN)
#         call = optionset.select_higher_volume(list_call)
#         if call is None:
#             return False
#         else:
#             print(optionset.eval_date, ' shift')
#             return True
#     else:
#         if k_call - spot <= 0.05 or k_put >= spot:
#             print(optionset.eval_date, ' shift')
#             return True
#         else:
#             return False
#
#
# def shift_three_way(df_index, put_long, put_short, call_short, spot, optionset):
#     dt_date = optionset.eval_date
#     if put_short is None or call_short is None:
#         maturity = optionset.select_maturity_date(nbr_maturity=0, min_holding=20)
#         std_close = df_index.loc[dt_date, 'std_close']
#         k_low = np.floor(put_long.strike() - std_close)
#         put_short = optionset.select_higher_volume(optionset.get_option_by_strike(c.OptionType.PUT, k_low, maturity))
#         k_high = np.floor(put_long.strike() + std_close)
#         call_short = optionset.select_higher_volume(optionset.get_option_by_strike(c.OptionType.CALL, k_high, maturity))
#         if call_short is not None and put_short is not None:
#             return True
#         else:
#             return False
#     else:
#         if spot > call_short.strike() or spot < put_short.strike():
#             return True
#         else:
#             return False

