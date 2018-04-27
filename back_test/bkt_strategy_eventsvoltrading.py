from back_test.bkt_strategy import BktOptionStrategy
from back_test.bkt_account import BktAccount
import QuantLib as ql
import numpy as np
import datetime
from back_test.bkt_util import BktUtil
from back_test.data_option import get_50option_mktdata2 as get_mktdata, get_eventsdata, get_50etf_mktdata
from back_test.OptionPortfolio import *
from Utilities.PlotUtil import PlotUtil
import matplotlib.pyplot as plt


class BktStrategyEventVol(BktOptionStrategy):

    def __init__(self, df_option_metrics, df_events, option_invest_pct=0.1):

        BktOptionStrategy.__init__(self, df_option_metrics,rf = 0.0)
        self.df_events = df_events.sort_values(by='dt_impact_beg', ascending=True).reset_index()
        self.moneyness = 0
        self.option_invest_pct = option_invest_pct
        self.cash_reserve_pct = 0.05
        self.delta_neutral = False
        self.portfolio = None

    def options_calendar_spread(self):
        bkt_optionset = self.bkt_optionset
        bkt = self.bkt_account
        idx_event = 0
        print(self.df_events)
        while bkt_optionset.index < len(bkt_optionset.dt_list):
            dt_event = self.df_events.loc[idx_event, 'dt_impact_beg']
            dt_volpeak = self.df_events.loc[idx_event, 'dt_vol_peak']
            cd_trade_deriction = self.df_events.loc[idx_event, 'cd_trade_direction']
            cd_open_position_time = self.df_events.loc[idx_event, 'cd_open_position_time']
            evalDate = bkt_optionset.eval_date

            df_metrics_today = bkt_optionset.df_daily_state

            """ 回测期最后一天全部清仓 """
            if evalDate == bkt_optionset.end_date:
                print(' Liquidate all positions !!! ')
                bkt.liquidate_all(evalDate)
                bkt.mkm_update(evalDate)
                print(evalDate, ' , ', bkt.npv)  # npv是组合净值，期初为1
                break

            """Option: Open position on event day, close on vol peak day"""
            cash_for_option = (1 - self.cash_reserve_pct) * bkt.cash
            if evalDate == dt_event:
                print(idx_event, ' ', evalDate, ' open position')

                if self.flag_trade:
                    print(evalDate, ' Trying to open position before previous one closed!')
                    return

                """Option: Select Strategy and Open Position"""
                mdt1 = self.get_1st_eligible_maturity(evalDate)
                mdt2 = self.get_2nd_eligible_maturity(evalDate)
                if cd_trade_deriction == -1:
                    df_open_position = self.bkt_optionset.get_calendar_spread_long(self.moneyness, mdt1, mdt2,
                                                                                   option_type=self.util.type_put)
                elif cd_trade_deriction == 1:
                    df_open_position = self.bkt_optionset.get_calendar_spread_long(self.moneyness, mdt1, mdt2,
                                                                                   option_type=self.util.type_call)
                else:
                    df_open_position = self.bkt_optionset.get_calendar_spread_long(self.moneyness, mdt1, mdt2)
                fund = 0
                for (idx, row) in df_open_position.iterrows():
                    bktoption = row[self.util.bktoption]
                    delta0_ratio = row[self.util.unit]
                    margin = bktoption.get_init_margin()  # 每手初始保证金
                    fund += margin * delta0_ratio
                unit = cash_for_option / fund
                # delta = 0
                for (idx, row) in df_open_position.iterrows():
                    bktoption = row[self.util.bktoption]
                    delta0_ratio = row[self.util.unit]
                    trade_unit = np.floor(delta0_ratio * unit)
                    # delta += bktoption.get_delta()*unit*delta0_ratio
                    if trade_unit > 0:
                        bkt.open_long(evalDate, unit=trade_unit, bktoption=bktoption)
                    else:
                        bkt.open_short(evalDate, unit=-trade_unit, bktoption=bktoption)

                    # self.holdings_mdt = bktoption.maturitydt
                self.flag_trade = True

            """Option: Close position """
            if evalDate == dt_volpeak:
                idx_event += 1
                if self.flag_trade:
                    print(idx_event, ' ', evalDate, ' close position')

                    self.flag_trade = False
                    for bktoption in bkt.holdings:
                        bkt.close_position(evalDate, bktoption)

            """按当日价格调整保证金，计算投资组合盯市价值"""
            bkt.mkm_update(evalDate)
            print(evalDate, bkt_optionset.eval_date, ' , ', bkt.npv)  # npv是组合净值，期初为1
            bkt_optionset.next()
            if idx_event >= len(self.df_events): break
        self.bkt_account1 = bkt

    def options_straddle(self):
        bkt_optionset = self.bkt_optionset
        bkt = self.bkt_account
        # bkt2 = BktAccount()
        idx_event = 0
        print(self.df_events)
        while bkt_optionset.index < len(bkt_optionset.dt_list):
            # dt_event = self.df_events.loc[idx_event, 'dt_impact_beg']
            dt_event = self.df_events.loc[idx_event, 'dt_test']
            # dt_volpeak = self.df_events.loc[idx_event, 'dt_vol_peak']
            dt_volpeak = self.df_events.loc[idx_event, 'dt_test2']
            cd_trade_deriction = self.df_events.loc[idx_event, 'cd_trade_direction']
            cd_open_position_time = self.df_events.loc[idx_event, 'cd_open_position_time']
            cd_close_position_time = self.df_events.loc[idx_event, 'cd_close_position_time']
            cd_open_position_time = 'morning_open_15min'
            cd_close_position_time = 'afternoon_close_15min'

            evalDate = bkt_optionset.eval_date

            if evalDate == datetime.date(2016,12,27):
                print(evalDate)
            """ 回测期最后一天全部清仓 """
            if evalDate == bkt_optionset.end_date:
                print(' Liquidate all positions !!! ')
                bkt.liquidate_all(evalDate)
                bkt.mkm_update(evalDate)
                print(evalDate, ' , ', bkt.npv)  # npv是组合净值，期初为1
                break

            """Option: Open position on event day, close on vol peak day"""
            if evalDate == dt_event:
                print(idx_event, ' ', evalDate, ' open position')

                if self.flag_trade:
                    print(evalDate, ' Trying to open position before previous one closed!')
                    return
                cash_for_option = (1 - self.cash_reserve_pct) * bkt.cash

                """Option: Select Strategy and Open Position"""
                # if cd_trade_deriction == -1:
                #     portfolio = self.bkt_optionset.get_put(self.moneyness,
                #                                                   self.get_1st_eligible_maturity(evalDate))  # 选择跨式期权头寸
                # elif cd_trade_deriction == 1:
                #     portfolio = self.bkt_optionset.get_call(self.moneyness, self.get_1st_eligible_maturity(evalDate))
                # else:
                #     portfolio = self.bkt_optionset.get_straddle(self.moneyness,
                #                                                        self.get_1st_eligible_maturity(evalDate))
                portfolio = self.bkt_optionset.get_straddle(self.moneyness,
                                                            self.get_1st_eligible_maturity(evalDate))
                # portfolio = self.bkt_optionset.get_call(0, self.get_1st_eligible_maturity(evalDate))
                print(portfolio.optionset[0].id_instrument,portfolio.optionset[0].dt_date,portfolio.optionset[0].underlying_price)
                # self.delta_neutral = True
                self.portfolio = portfolio
                self.bkt_account.update_invest_units(portfolio, self.util.long, cd_open_position_time,
                                                     fund=cash_for_option)
                bkt.open_long(evalDate, portfolio, cd_open_by_price=cd_open_position_time)
                self.flag_trade = True
            elif evalDate != dt_volpeak:
                if self.flag_trade:
                    if isinstance(self.portfolio, Straddle):  # DELTA NEUTRAL REBALANCING
                        """ Rebalance Straddle on delta neutral """
                        self.bkt_account.update_invest_units(self.portfolio, self.util.long)
                        bkt.rebalance_position(evalDate, self.portfolio)

            if evalDate == dt_volpeak:
                idx_event += 1
                if self.flag_trade:
                    print(idx_event, ' ', evalDate, ' close position')
                    """ Close position"""
                    self.flag_trade = False
                    self.delta_neutral = False
                    for bktoption in bkt.holdings:
                        bkt.close_position(evalDate, bktoption, cd_close_by_price=cd_close_position_time)

            """按当日价格调整保证金，计算投资组合盯市价值"""
            bkt.mkm_update(evalDate)
            print(evalDate, bkt_optionset.eval_date, ' , ', bkt.npv)  # npv是组合净值，期初为1
            bkt_optionset.next()
            if idx_event >= len(self.df_events): break

    def options_straddle_etf(self):
        bkt_optionset = self.bkt_optionset
        bkt = self.bkt_account
        bkt2 = BktAccount()
        idx_event = 0
        print(self.df_events)
        while bkt_optionset.index < len(bkt_optionset.dt_list):
            dt_event = self.df_events.loc[idx_event, 'dt_impact_beg']
            dt_volpeak = self.df_events.loc[idx_event, 'dt_vol_peak']
            cd_trade_deriction = self.df_events.loc[idx_event, 'cd_trade_direction']
            cd_open_position_time = self.df_events.loc[idx_event, 'cd_open_position_time']
            cd_close_position_time = self.df_events.loc[idx_event, 'cd_close_position_time']

            evalDate = bkt_optionset.eval_date
            df_metrics_today = bkt_optionset.df_daily_state

            """ 50ETF仓位: track index """
            etf_price = df_metrics_today.loc[0, self.util.col_underlying_price]
            trade_order_dict = {'id_instrument': 'index_50etf', 'dt_date': evalDate, 'price': etf_price }
            trade_order_dict2 = { 'id_instrument': 'index_50etf', 'dt_date': evalDate, 'price': etf_price}

            """ 回测期最后一天全部清仓 """
            if evalDate == bkt_optionset.end_date:
                print(' Liquidate all positions !!! ')
                bkt.liquidate_all(evalDate)
                bkt.mkm_update(evalDate, trade_order_dict)
                bkt2.liquidate_all(evalDate)
                bkt2.mkm_update(evalDate, trade_order_dict2)
                print(evalDate, ' , ', bkt.npv)  # npv是组合净值，期初为1
                break

            """ 开仓 50ETF """
            if bkt_optionset.index == 0:
                fund_etf = bkt.cash * (1 - self.option_invest_pct - self.cash_reserve_pct) * (1 - bkt.fee)
                unit = np.floor(fund_etf / etf_price)
                trade_order_dict.update({'unit': unit})
                bkt.open_long(evalDate, trade_order_dict)
                fund_etf2 = bkt2.cash * (1 - self.cash_reserve_pct) * (1 - bkt2.fee)
                unit2 = np.floor(fund_etf2 / etf_price)
                trade_order_dict2.update({'unit': unit2})
                bkt2.open_long(evalDate, trade_order_dict2)
            else:  # """ 根据投资比例调整50ETF仓位"""
                etf_invest = bkt.trade_order_mktv / bkt.total_asset
                etf_ratio = 1 - self.option_invest_pct - self.cash_reserve_pct
                if etf_invest > etf_ratio + 0.01 or etf_invest < etf_ratio - 0.01:
                    fund_etf = bkt.total_asset * (1 - self.option_invest_pct) * (1 - bkt.fee)
                    unit = np.floor(fund_etf / etf_price)
                    trade_order_dict.update({'unit': unit})
                    bkt.rebalance_position(evalDate, trade_order_dict)

            """Option: Open position on event day, close on vol peak day"""
            if evalDate == dt_event:
                print(idx_event, ' ', evalDate, ' open position')

                if self.flag_trade:
                    print(evalDate, ' Trying to open position before previous one closed!')
                    return
                cash_for_option = (1 - self.cash_reserve_pct) * bkt.cash

                """Option: Select Strategy and Open Position"""
                if cd_trade_deriction == -1:
                    portfolio = self.bkt_optionset.get_put(self.moneyness,
                                                                  self.get_1st_eligible_maturity(evalDate))  # 选择跨式期权头寸
                elif cd_trade_deriction == 1:
                    portfolio = self.bkt_optionset.get_call(self.moneyness, self.get_1st_eligible_maturity(evalDate))
                else:
                    portfolio = self.bkt_optionset.get_straddle(self.moneyness,
                                                                       self.get_1st_eligible_maturity(evalDate))
                # portfolio = self.bkt_optionset.get_straddle(self.moneyness,
                #                                             self.get_1st_eligible_maturity(evalDate))

                # self.delta_neutral = True
                self.portfolio = portfolio
                self.bkt_account.update_invest_units(portfolio, self.util.long, cd_open_position_time,
                                                     fund=cash_for_option)
                bkt.open_long(evalDate, portfolio, cd_open_by_price=cd_open_position_time)
                self.flag_trade = True
            elif evalDate != dt_volpeak:
                if self.flag_trade:
                    if isinstance(self.portfolio, Straddle):  # DELTA NEUTRAL REBALANCING
                        """ Rebalance Straddle on delta neutral """
                        self.bkt_account.update_invest_units(self.portfolio, self.util.long)
                        bkt.rebalance_position(evalDate, self.portfolio)

            if evalDate == dt_volpeak:
                idx_event += 1
                if self.flag_trade:
                    print(idx_event, ' ', evalDate, ' close position')
                    """ Close position"""
                    self.flag_trade = False
                    self.delta_neutral = False
                    for bktoption in bkt.holdings:
                        bkt.close_position(evalDate, bktoption, cd_close_by_price=cd_close_position_time)

            """按当日价格调整保证金，计算投资组合盯市价值"""
            bkt.mkm_update(evalDate, trade_order_dict=trade_order_dict)
            bkt2.mkm_update(evalDate, trade_order_dict=trade_order_dict2)
            print(evalDate, bkt_optionset.eval_date, ' , ', bkt.npv)  # npv是组合净值，期初为1
            bkt_optionset.next()
            if idx_event >= len(self.df_events): break
            self.bkt_account1 = bkt
            self.bkt_account2 = bkt2

    def etf_enhanced_by_options(self):
        bkt_optionset = self.bkt_optionset
        bkt = self.bkt_account
        bkt2 = BktAccount()
        idx_event = 0
        print(self.df_events)
        while bkt_optionset.index < len(bkt_optionset.dt_list):
            dt_event = self.df_events.loc[idx_event, 'dt_impact_beg']
            dt_volpeak = self.df_events.loc[idx_event, 'dt_vol_peak']
            cd_trade_deriction = self.df_events.loc[idx_event, 'cd_trade_direction']
            evalDate = bkt_optionset.eval_date

            df_metrics_today = bkt_optionset.df_daily_state

            """ 50ETF仓位: track index """
            etf_price = df_metrics_today.loc[0, self.util.col_underlying_price]
            trade_order_dict = {
                'id_instrument': 'index_50etf',
                'dt_date': evalDate,
                'price': etf_price,
            }
            trade_order_dict2 = {
                'id_instrument': 'index_50etf',
                'dt_date': evalDate,
                'price': etf_price}

            """ 回测期最后一天全部清仓 """
            if evalDate == bkt_optionset.end_date:
                print(' Liquidate all positions !!! ')
                bkt.liquidate_all(evalDate)
                bkt.mkm_update(evalDate, trade_order_dict)
                bkt2.liquidate_all(evalDate)
                bkt2.mkm_update(evalDate, trade_order_dict2)
                print(evalDate, ' , ', bkt.npv)  # npv是组合净值，期初为1
                break
            # """ 开仓 50ETF """
            if bkt_optionset.index == 0:
                fund_etf = bkt.cash * (1 - self.option_invest_pct - self.cash_reserve_pct) * (1 - bkt.fee)
                unit = np.floor(fund_etf / etf_price)
                trade_order_dict.update({'unit': unit})
                bkt.open_long(evalDate, trade_order_dict=trade_order_dict)
                fund_etf2 = bkt2.cash * (1 - self.cash_reserve_pct) * (1 - bkt2.fee)
                unit2 = np.floor(fund_etf2 / etf_price)
                trade_order_dict2.update({'unit': unit2})
                bkt2.open_long(evalDate, trade_order_dict=trade_order_dict2)
            else:  # """ 根据投资比例调整50ETF仓位"""
                etf_invest = bkt.margin_trade_order / bkt.total_asset
                etf_ratio = 1 - self.option_invest_pct - self.cash_reserve_pct
                if etf_invest > etf_ratio + 0.01 or etf_invest < etf_ratio - 0.01:
                    fund_etf = bkt.total_asset * (1 - self.option_invest_pct) * (1 - bkt.fee)
                    unit = np.floor(fund_etf / etf_price)
                    trade_order_dict.update({'unit': unit})
                    bkt.rebalance_position(evalDate, trade_order_dict=trade_order_dict)

            """Option: Open position on event day, close on vol peak day"""
            cash_for_option = (1 - self.cash_reserve_pct) * bkt.cash
            if evalDate == dt_event:
                print(idx_event, ' ', evalDate, ' open position')

                if self.flag_trade:
                    print(evalDate, ' Trying to open position before previous one closed!')
                    return

                """Option: Select Strategy and Open Position"""

                if cd_trade_deriction == -1:
                    df_open_position = self.bkt_optionset.get_put(self.moneyness,
                                                                  self.get_1st_eligible_maturity(evalDate))  # 选择跨式期权头寸
                elif cd_trade_deriction == 1:
                    df_open_position = self.bkt_optionset.get_call(self.moneyness,
                                                                   self.get_1st_eligible_maturity(evalDate))
                else:
                    df_open_position = self.bkt_optionset.get_straddle(self.moneyness,
                                                                       self.get_1st_eligible_maturity(evalDate))
                fund = 0
                for (idx, row) in df_open_position.iterrows():
                    bktoption = row[self.util.bktoption]
                    delta0_ratio = row[self.util.unit]
                    margin = bktoption.get_init_margin()  # 每手初始保证金
                    fund += margin * delta0_ratio
                unit = cash_for_option / fund
                # delta = 0
                for (idx, row) in df_open_position.iterrows():
                    bktoption = row[self.util.bktoption]
                    delta0_ratio = row[self.util.unit]
                    trade_unit = np.floor(delta0_ratio * unit)
                    # delta += bktoption.get_delta()*unit*delta0_ratio
                    bkt.open_long(evalDate, unit=trade_unit, bktoption=bktoption)
                    self.holdings_mdt = bktoption.maturitydt
                self.flag_trade = True

            """Option: Close position """
            if evalDate == dt_volpeak:
                idx_event += 1
                if self.flag_trade:
                    print(idx_event, ' ', evalDate, ' close position')
                    self.flag_trade = False
                    for bktoption in bkt.holdings:
                        bkt.close_position(evalDate, bktoption)

            """按当日价格调整保证金，计算投资组合盯市价值"""
            bkt.mkm_update(evalDate, trade_order_dict=trade_order_dict)
            bkt2.mkm_update(evalDate, trade_order_dict=trade_order_dict2)
            print(evalDate, bkt_optionset.eval_date, ' , ', bkt.npv)  # npv是组合净值，期初为1
            bkt_optionset.next()
            if idx_event >= len(self.df_events): break
        self.bkt_account1 = bkt
        self.bkt_account2 = bkt2


"""Back Test Settings"""
start_date = datetime.date(2017, 5, 13)
end_date = datetime.date(2017, 9, 30)
calendar = ql.China()
daycounter = ql.ActualActual()
util = BktUtil()

"""Collect Mkt Date"""
df_events = get_eventsdata(start_date, end_date,1)

df_option_metrics = get_mktdata(start_date, end_date)
# df_etf_metrics = get_50etf_mktdata(start_date,end_date)

"""Run Backtest"""

bkt_strategy = BktStrategyEventVol(df_option_metrics, df_events, option_invest_pct=0.2)
bkt_strategy.set_min_holding_days(20)

# bkt_strategy.options_straddle_etf()
# npv1 = bkt_strategy.bkt_account1.df_account['npv'].tolist()
# npv2 = bkt_strategy.bkt_account2.df_account['npv'].tolist()
#
# pu = PlotUtil()
# dates = bkt_strategy.bkt_account1.df_account['dt_date'].unique()
# f = pu.plot_line_chart(dates, [npv1,npv2], ['85% 50etf & 10% option & 5% cash','50etf'])
# plt.show()

bkt_strategy.options_straddle()
# # bkt_strategy.options_calendar_spread()
#
#
bkt_strategy.bkt_account.df_account.to_csv('../save_results/df_account.csv')
bkt_strategy.bkt_account.df_trading_book.to_csv('../save_results/df_trading_book.csv')
bkt_strategy.bkt_account.df_trading_records.to_csv('../save_results/df_trading_records.csv')

# bkt_strategy.return_analysis()
