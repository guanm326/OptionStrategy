import typing
import math
import datetime
from scipy.stats import norm
import back_test.model.constant as constant
import back_test.model.constant as c
from PricingLibrary.AbstractOptionPricingEngine import AbstractOptionPricingEngine
from back_test.model.constant import OptionType,PricingUtil


class OptionPayoff(object):
    @staticmethod
    def get_payoff(s: float, k: float):
        return max(s - k, 0)


class Binomial(AbstractOptionPricingEngine):

    def __init__(self,
                 dt_eval: datetime.date,
                 dt_maturity: datetime.date,
                 option_type: constant.OptionType,
                 option_exercise_type: constant.OptionExerciseType,
                 spot: float,
                 strike: float,
                 vol: float = 0.2,
                 rf: float = 0.03,
                 n: int=800):
        super().__init__()
        self.values: typing.List[typing.List[float]] = []
        self.asset_values: typing.List[typing.List[float]] = []
        self.exercise_values: typing.List[typing.List[float]] = []
        self.option_type = option_type
        self.option_exercise_type = option_exercise_type
        self.strike = strike
        self.spot = spot
        self.rf = rf
        self.dt_eval: datetime.date = dt_eval
        self.dt_maturity: datetime.date = dt_maturity
        self.T: float = (dt_maturity - dt_eval).days / 365.0
        self.t: float = self.T/n
        self.u = math.exp(vol * math.sqrt(self.t))
        self.d = math.exp(-1 * vol * math.sqrt(self.t))
        self.p_u = (math.exp(rf * self.t) - self.d) / (self.u - self.d)
        self.p_d = 1 - self.p_u
        self.discount = math.exp(-1 * rf * self.t)
        self.n: int = n

    def initialize(self):
        self.populate_asset()

    def populate_asset(self):
        pre = []
        for i in range(self.n):
            if len(pre) == 0:
                cur = [self.spot]
            else:
                cur = [pre[0] * self.u]
                for item in pre:
                    cur.append(item * self.d)
            self.asset_values.append(cur)
            pre = cur
        for asset_value in self.asset_values:
            exercise_value = [constant.PricingUtil.payoff(v, self.strike, self.option_type) for v in asset_value]
            self.exercise_values.append(exercise_value)

    def disp(self):
        print("exercise type =", self.option_exercise_type)
        print("u =", self.u)
        print("d =", self.d)
        print("p_u =", self.p_u)
        print("p_d =", self.p_d)

    def size(self, i: int) -> int:
        return i

    def NPV(self) -> float:
        self.step_back(0)
        return self.values[0][0]

    def step_back(self, step_back_to: int) -> None:
        step_back_from = self.n - 1
        self.values.insert(0, self.exercise_values[step_back_from])
        for i in range(step_back_from, step_back_to, -1):
            cur_value = self.values[0]
            pre_value = []
            count = self.size(i)
            for j in range(count):
                continous_value = (cur_value[j] * self.p_u + cur_value[j + 1] * self.p_d) * self.discount
                if self.option_exercise_type == constant.OptionExerciseType.AMERICAN:
                    exercise_value = self.exercise_values[i - 1][j]
                else:
                    exercise_value = 0
                pre_value.append(max(continous_value, exercise_value))
            self.values.insert(0, pre_value)
        return None

    def reset(self, vol: float) -> None:
        self.asset_values = []
        self.values = []
        self.exercise_values = []
        self.u = math.exp(vol * math.sqrt(self.t))
        self.d = math.exp(-1 * vol * math.sqrt(self.t))
        self.p_u = (math.exp(self.rf * self.t) - self.d) / (self.u - self.d)
        self.p_d = 1 - self.p_u
        self.discount = math.exp(-1 * self.rf * self.t)
        self.populate_asset()

    def estimate_vol(self, price: float, presion:float=0.00001,max_vol:float=2.0):
        l = presion
        r = max_vol
        while l < r and round((r - l), 5) > presion:
            m = round(l + (r - l) / 2, 5)
            self.reset(m)
            p = self.NPV()
            if p < price:
                l = m
            else:
                r = m
        return m




class BlackFormula(AbstractOptionPricingEngine):


    def __init__(self,
                 dt_eval: datetime.date,
                 dt_maturity: datetime.date,
                 option_type: constant.OptionType,
                 spot: float,
                 strike: float,
                 vol: float = 0.0,
                 rf: float = 0.03,
                 dividend_rate: float = 0.0):
        super().__init__()
        discount = PricingUtil.get_discount(dt_eval, dt_maturity, rf)
        self.dt_eval = dt_eval
        self.dt_maturity = dt_maturity
        self.option_type = option_type
        self.strike = strike
        self.forward = spot / discount
        self.discount = discount
        self.spot = spot
        self.vol = vol
        self.rf = rf
        self.dividend_rate = dividend_rate


    def reset_vol(self, vol):
        self.vol = vol
        stdDev = PricingUtil.get_std(self.dt_eval, self.dt_maturity, vol)
        self.stdDev = stdDev
        if stdDev > 0.0:
            if self.strike == 0.0:
                n_d1 = 0.0
                n_d2 = 0.0
                cum_d1 = 1.0
                cum_d2 = 1.0
                D1 = None
                D2 = None
            else:
                D1 = math.log(self.forward / self.strike, math.e) / stdDev + 0.5 * stdDev
                D2 = D1 - stdDev
                cum_d1 = norm.cdf(D1)
                cum_d2 = norm.cdf(D2)
                n_d1 = norm.pdf(D1)
                n_d2 = norm.pdf(D2)
            self.D1 = D1
            self.D2 = D2
        else:
            if self.forward > self.strike:
                cum_d1 = 1.0
                cum_d2 = 1.0
            else:
                cum_d1 = 0.0
                cum_d2 = 0.0
            n_d1 = 0.0
            n_d2 = 0.0

        # if self.iscall:
        if self.option_type == c.OptionType.CALL:
            alpha = cum_d1  ## N(d1)
            dAlpha_dD1 = n_d1  ## n(d1)
            beta = -cum_d2  ## -N(d2)
            dBeta_dD2 = -n_d2  ## -n(d2)
        else:
            alpha = -1.0 + cum_d1  ## -N(-d1)
            dAlpha_dD1 = n_d1  ## n( d1)
            beta = 1.0 - cum_d2  ## N(-d2)
            dBeta_dD2 = -n_d2  ## -n( d2)
        self.alpha = alpha
        self.dAlpha_dD1 = dAlpha_dD1
        self.beta = beta
        self.dBeta_dD2 = dBeta_dD2
        self.x = self.strike
        self.dX_dS = 0.0








