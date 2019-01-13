import numpy as np
from PricingLibrary.EngineQuantlib import QlBlackFormula,QlBinomial
from PricingLibrary.Options import EuropeanOption
from back_test.model.base_future_coutinuous import BaseFutureCoutinuous
from back_test.model.base_future_set import BaseFutureSet
from back_test.model.constant import Util, FrequentType, DeltaBound, BuyWrite
from PricingLibrary.Util import PricingUtil
import math


class SytheticOption(BaseFutureCoutinuous):

    """
    基于期货主力合约的对冲组合/合成期权：用于指数/ETF【欧式】期权
    """

    def __init__(self, df_c1_data,rf,
                 df_c1_daily=None,
                 df_futures_all_daily=None,
                 df_index_daily=None,
                 frequency=FrequentType.DAILY
                 ):
        super().__init__(df_future_c1=df_c1_data, df_future_c1_daily=df_c1_daily,
                         df_futures_all_daily=df_futures_all_daily, df_underlying_index_daily=df_index_daily,
                         frequency=frequency)
        self.synthetic_unit = 0
        self.amt_option = 1
        self.rf = rf

    def get_c1_with_start_dates(self):
        df = self.df_daily_data.drop_duplicates(Util.ID_INSTRUMENT)[[Util.DT_DATE, Util.ID_INSTRUMENT]]
        return df

    def get_c1_with_end_dates(self):
        df = self.df_daily_data.drop_duplicates(Util.ID_INSTRUMENT, 'last')[[Util.DT_DATE, Util.ID_INSTRUMENT]]
        return df

    def get_black_delta(self, option: EuropeanOption, vol: float, spot: float = None):
        if spot is None:
            spot = self.mktprice_close()
        black = QlBlackFormula(dt_eval=self.eval_date, dt_maturity=option.dt_maturity,
                               option_type=option.option_type, spot=spot,
                               strike=option.strike, vol=vol, rf=self.rf)
        delta = black.Delta(vol)
        return delta

    # Get synthetic position in trade unit
    def get_synthetic_unit(self, delta, buywrite=BuyWrite.BUY) -> int:
        trade_unit = np.floor(buywrite.value * delta * self.amt_option / self.multiplier())
        return trade_unit

    # Get hedge position in trade unit
    def get_hedge_position(self, delta, buywrite=BuyWrite.BUY):
        # hedge_scale : total notional amt to hedge in RMB
        return - self.get_synthetic_unit(delta, buywrite)

    def get_hedge_rebalancing_unit(self, delta: float,
                                   buywrite: BuyWrite = BuyWrite.BUY) -> int:
        hold_unit = self.synthetic_unit
        synthetic_unit = self.get_synthetic_unit(delta, buywrite)
        d_unit = -(synthetic_unit - hold_unit)
        return d_unit
        # if delta_bound == DeltaBound.WHALLEY_WILLMOTT:
        #     if vol is None or spot is None or gamma is None or dt_maturity is None: return
        #     bound = self.whalley_wilmott2(self.eval_date, vol, spot, gamma, dt_maturity) * self.amt_option / self.multiplier()
        #     if abs(d_unit) > bound:
        #         return d_unit
        #     else:
        #         return 0
        # else:
        #     return d_unit

    def get_rebalancing_unit(self, delta: float,
                             option: EuropeanOption,
                             vol: float,
                             spot: float,
                             delta_bound: DeltaBound,
                             buywrite: BuyWrite = BuyWrite.BUY) -> int:
        hold_unit = self.synthetic_unit
        synthetic_unit = self.get_synthetic_unit(delta, buywrite)
        d_unit = synthetic_unit - hold_unit
        if delta_bound == DeltaBound.WHALLEY_WILLMOTT:
            bound = self.whalley_wilmott(self.eval_date, option, vol, spot) * self.amt_option / self.multiplier()
            if abs(d_unit) > bound:
                return d_unit
            else:
                return 0
        else:
            return d_unit

    def whalley_wilmott(self, eval_date, option, vol, spot=None, rho=0.5, fee=6.9 / 10000.0):
        if spot is None:
            spot = self.mktprice_close()
        black = QlBlackFormula(dt_eval=self.eval_date, dt_maturity=option.dt_maturity,
                               option_type=option.option_type, spot=spot,
                               strike=option.strike, vol=vol, rf=self.rf)
        gamma = black.Gamma(vol)
        ttm = PricingUtil.get_ttm(eval_date, option.dt_maturity)
        H = (1.5 * math.exp(-self.rf * ttm) * fee * spot * (gamma ** 2) / rho) ** (1 / 3)
        return H

    def whalley_wilmott2(self, eval_date, vol, spot, gamma, dt_maturity, rho=0.5, fee=6.9 / 10000.0):
        ttm = PricingUtil.get_ttm(eval_date, dt_maturity)
        H = (1.5 * math.exp(-self.rf * ttm) * fee * spot * (gamma ** 2) / rho) ** (1 / 3)
        return H


    def replicated_option_value(self, option: EuropeanOption, vol):
        spot = self.mktprice_close()
        black = QlBlackFormula(self.eval_date, option.dt_maturity, option.strike,
                               option.option_type, spot, vol, self.rf)
        npv = black.NPV()
        return npv


class SytheticOption_AmeComdty(BaseFutureSet):

    """
    基于期货主力合约的对冲组合/合成期权：用于【美式】期货期权：豆粕白糖等
    """

    def __init__(self, df_data,rf,
                 df_daily_data=None,
                 frequency=FrequentType.DAILY
                 ):
        super().__init__(df_data=df_data, df_daily_data=df_daily_data, frequency=frequency)
        self.synthetic_unit = 0
        self.amt_option = 1
        self.rf = rf

    def get_black_delta(self, option: EuropeanOption, vol: float, spot: float = None):
        if spot is None:
            spot = self.mktprice_close()
        black = QlBlackFormula(dt_eval=self.eval_date, dt_maturity=option.dt_maturity,
                               option_type=option.option_type, spot=spot,
                               strike=option.strike, vol=vol, rf=self.rf)
        delta = black.Delta(vol)
        return delta

    # Get synthetic position in trade unit
    def get_synthetic_unit(self, delta, buywrite=BuyWrite.BUY) -> int:
        trade_unit = np.floor(buywrite.value * delta * self.amt_option / self.multiplier())
        return trade_unit

    # Get hedge position in trade unit
    def get_hedge_position(self, delta, buywrite=BuyWrite.BUY):
        # hedge_scale : total notional amt to hedge in RMB
        return - self.get_synthetic_unit(delta, buywrite)

    def get_hedge_rebalancing_unit(self, delta: float,
                                   buywrite: BuyWrite = BuyWrite.BUY) -> int:
        hold_unit = self.synthetic_unit
        synthetic_unit = self.get_synthetic_unit(delta, buywrite)
        d_unit = -(synthetic_unit - hold_unit)
        return d_unit
        # if delta_bound == DeltaBound.WHALLEY_WILLMOTT:
        #     if vol is None or spot is None or gamma is None or dt_maturity is None: return
        #     bound = self.whalley_wilmott2(self.eval_date, vol, spot, gamma, dt_maturity) * self.amt_option / self.multiplier()
        #     if abs(d_unit) > bound:
        #         return d_unit
        #     else:
        #         return 0
        # else:
        #     return d_unit

    def get_rebalancing_unit(self, delta: float,
                             option: EuropeanOption,
                             vol: float,
                             spot: float,
                             delta_bound: DeltaBound,
                             buywrite: BuyWrite = BuyWrite.BUY) -> int:
        hold_unit = self.synthetic_unit
        synthetic_unit = self.get_synthetic_unit(delta, buywrite)
        d_unit = synthetic_unit - hold_unit
        if delta_bound == DeltaBound.WHALLEY_WILLMOTT:
            bound = self.whalley_wilmott(self.eval_date, option, vol, spot) * self.amt_option / self.multiplier()
            if abs(d_unit) > bound:
                return d_unit
            else:
                return 0
        else:
            return d_unit

    def whalley_wilmott(self, eval_date, option, vol, spot=None, rho=0.5, fee=6.9 / 10000.0):
        if spot is None:
            spot = self.mktprice_close()
        black = QlBlackFormula(dt_eval=self.eval_date, dt_maturity=option.dt_maturity,
                               option_type=option.option_type, spot=spot,
                               strike=option.strike, vol=vol, rf=self.rf)
        gamma = black.Gamma(vol)
        ttm = PricingUtil.get_ttm(eval_date, option.dt_maturity)
        H = (1.5 * math.exp(-self.rf * ttm) * fee * spot * (gamma ** 2) / rho) ** (1 / 3)
        return H

    def whalley_wilmott2(self, eval_date, vol, spot, gamma, dt_maturity, rho=0.5, fee=6.9 / 10000.0):
        ttm = PricingUtil.get_ttm(eval_date, dt_maturity)
        H = (1.5 * math.exp(-self.rf * ttm) * fee * spot * (gamma ** 2) / rho) ** (1 / 3)
        return H


    def replicated_option_value(self, option: EuropeanOption, vol):
        spot = self.mktprice_close()
        black = QlBlackFormula(self.eval_date, option.dt_maturity, option.strike,
                               option.option_type, spot, vol, self.rf)
        npv = black.NPV()
        return npv
