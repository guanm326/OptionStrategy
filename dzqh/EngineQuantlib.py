import typing
import datetime
import dzqh.constant as constant
import QuantLib as ql
from dzqh.AbstractOptionPricingEngine import AbstractOptionPricingEngine

"""
                 dt_eval: evaluation date,
                 dt_maturity: option maturity date,
                 option_type: call/put,
                 option_exercise_type: American/European,
                 strike: option strike price,
                 spot: underlying price,
                 vol: volatility,
                 rf: risk free rate,
                 dividend_date: underlying dividend rate,
                 n: Binomial pricing model steps
"""

class QlBAW(AbstractOptionPricingEngine):
    def __init__(self,
                 dt_eval: datetime.date,
                 dt_maturity: datetime.date,
                 option_type: constant.OptionType,
                 option_exercise_type: constant.OptionExerciseType,
                 spot: float,
                 strike: float,
                 vol: float = 0.2,
                 rf: float = 0.03,
                 dividend_rate: float = 0.0):
        super().__init__()
        self.strike = strike
        self.spot = spot
        self.vol = vol
        self.rf = rf
        self.dividend_rate = dividend_rate
        self.maturity_date = constant.QuantlibUtil.to_ql_date(dt_maturity)
        self.settlement = constant.QuantlibUtil.to_ql_date(dt_eval)
        ql.Settings.instance().evaluationDate = self.settlement
        if option_type == constant.OptionType.PUT:
            self.option_type = ql.Option.Put
        else:
            self.option_type = ql.Option.Call
        payoff = ql.PlainVanillaPayoff(self.option_type, strike)
        if option_exercise_type == constant.OptionExerciseType.AMERICAN:
            self.exercise = ql.AmericanExercise(self.settlement, self.maturity_date)
            self.ql_option = ql.VanillaOption(payoff, self.exercise)
        else:
            self.exercise = ql.EuropeanExercise(self.maturity_date)
            self.ql_option = ql.VanillaOption(payoff, self.exercise)
        self.day_count = ql.ActualActual()
        self.calendar = ql.China()
        self.spot_handle = ql.QuoteHandle(ql.SimpleQuote(spot))
        self.flat_ts = ql.YieldTermStructureHandle(
            ql.FlatForward(self.settlement, rf, self.day_count)
        )
        self.dividend_yield = ql.YieldTermStructureHandle(
            ql.FlatForward(self.settlement, self.dividend_rate, self.day_count)
        )
        self.flat_vol_ts = ql.BlackVolTermStructureHandle(
            ql.BlackConstantVol(self.settlement, self.calendar, self.vol, self.day_count)
        )
        self.bsm_process = ql.BlackScholesMertonProcess(self.spot_handle,
                                                        self.dividend_yield,
                                                        self.flat_ts,
                                                        self.flat_vol_ts)
        engine = ql.BaroneAdesiWhaleyEngine(self.bsm_process)
        self.ql_option.setPricingEngine(engine)

    def NPV(self) -> float:
        return self.ql_option.NPV()

    def Delta(self,implied_vol:float=None) -> float:
        if implied_vol is not None: self.reset_vol(implied_vol)
        try: delta = self.ql_option.delta()
        except:
            delta = 0.0
        return delta

    def Gamma(self,implied_vol:float=None) -> float:
        if implied_vol is not None: self.reset_vol(implied_vol)
        try: gamma = self.ql_option.gamma()
        except:
            gamma = 0.0
        return gamma

    def Theta(self,implied_vol:float=None) -> float:
        if implied_vol is not None: self.reset_vol(implied_vol)
        try:
            theta = self.ql_option.theta()/365.0
        except:
            theta=0.0
        return theta

    def Vega(self,implied_vol:float=None) -> float:
        if implied_vol is not None: self.reset_vol(implied_vol)
        try:
            vega = self.ql_option.vega()/100.0
        except:
            vega=0.0
        return vega

    def reset_vol(self, vol):
        self.vol = vol
        self.flat_vol_ts = ql.BlackVolTermStructureHandle(
            ql.BlackConstantVol(self.settlement, self.calendar, vol, self.day_count)
        )
        self.bsm_process = ql.BlackScholesMertonProcess(self.spot_handle,
                                                        self.dividend_yield,
                                                        self.flat_ts,
                                                        self.flat_vol_ts)
        engine = ql.BaroneAdesiWhaleyEngine(self.bsm_process)
        self.ql_option.setPricingEngine(engine)

    def estimate_vol_ql(self, targetValue: float, accuracy=1.0e-4, maxEvaluations=100, minVol=1.0e-4, maxVol=4.0):
        try:
            implied_vol = self.ql_option.impliedVolatility(targetValue, self.bsm_process, accuracy, maxEvaluations,
                                                               minVol, maxVol)
        except Exception as e:
            print(e)
            implied_vol = None
        return implied_vol

    def estimate_vol(self, price: float, presion: float = 0.00001,min_vol=0.01, max_vol: float = 2.0):
        l = min_vol
        r = max_vol
        while l < r and round((r - l), 5) > presion:
            m = round(l + (r - l) / 2, 5)
            self.reset_vol(m)
            p = self.NPV()
            if p < price:
                l = m
            else:
                r = m
        return m



class QlBinomial(AbstractOptionPricingEngine):
    def __init__(self,
                 dt_eval: datetime.date,
                 dt_maturity: datetime.date,
                 option_type: constant.OptionType,
                 option_exercise_type: constant.OptionExerciseType,
                 spot: float,
                 strike: float,
                 vol: float = 0.2,
                 rf: float = 0.03,
                 n: int = 801,
                 dividend_rate: float = 0.0):
        super().__init__()
        self.values: typing.List[typing.List[float]] = []
        self.asset_values: typing.List[typing.List[float]] = []
        self.exercise_values: typing.List[typing.List[float]] = []
        self.strike = strike
        self.spot = spot
        self.vol = vol
        self.rf = rf
        self.dividend_rate = dividend_rate
        self.steps: int = n
        self.maturity_date = constant.QuantlibUtil.to_ql_date(dt_maturity)
        self.settlement = constant.QuantlibUtil.to_ql_date(dt_eval)
        ql.Settings.instance().evaluationDate = self.settlement
        if option_type == constant.OptionType.PUT:
            self.option_type = ql.Option.Put
        else:
            self.option_type = ql.Option.Call
        payoff = ql.PlainVanillaPayoff(self.option_type, strike)
        if option_exercise_type == constant.OptionExerciseType.AMERICAN:
            self.exercise = ql.AmericanExercise(self.settlement, self.maturity_date)
            self.ql_option = ql.VanillaOption(payoff, self.exercise)
        else:
            self.exercise = ql.EuropeanExercise(self.maturity_date)
            self.ql_option = ql.VanillaOption(payoff, self.exercise)
        self.day_count = ql.ActualActual()
        self.calendar = ql.China()
        self.spot_handle = ql.QuoteHandle(ql.SimpleQuote(spot))
        self.flat_ts = ql.YieldTermStructureHandle(
            ql.FlatForward(self.settlement, rf, self.day_count)
        )
        self.dividend_yield = ql.YieldTermStructureHandle(
            ql.FlatForward(self.settlement, self.dividend_rate, self.day_count)
        )
        self.flat_vol_ts = ql.BlackVolTermStructureHandle(
            ql.BlackConstantVol(self.settlement, self.calendar, self.vol, self.day_count)
        )
        self.bsm_process = ql.BlackScholesMertonProcess(self.spot_handle,
                                                        self.dividend_yield,
                                                        self.flat_ts,
                                                        self.flat_vol_ts)
        binomial_engine = ql.BinomialVanillaEngine(self.bsm_process, "crr", self.steps)
        self.ql_option.setPricingEngine(binomial_engine)

    def NPV(self) -> float:
        return self.ql_option.NPV()

    def Delta(self,implied_vol:float=None) -> float:
        if implied_vol is not None: self.reset_vol(implied_vol)
        return self.ql_option.delta()

    def Gamma(self,implied_vol:float=None) -> float:
        if implied_vol is not None: self.reset_vol(implied_vol)
        return self.ql_option.gamma()

    def Theta(self,implied_vol:float=None) -> float:
        if implied_vol is not None: self.reset_vol(implied_vol)
        try:
            theta = self.ql_option.theta()/365.0
        except:
            theta=0.0
        return theta

    def Vega(self,implied_vol:float=None) -> float:
        vega=self.vega_effective(implied_vol)
        return vega

    def vega_effective(self,implied_vol:float=None) -> float:
        if implied_vol is not None: self.reset_vol(implied_vol)
        price1 = self.NPV()
        self.reset_vol(self.vol+0.01)
        price2 = self.NPV()
        vega = price2 - price1
        return vega

    def reset_vol(self, vol):
        self.vol = vol
        self.flat_vol_ts = ql.BlackVolTermStructureHandle(
            ql.BlackConstantVol(self.settlement, self.calendar, vol, self.day_count)
        )
        self.bsm_process = ql.BlackScholesMertonProcess(self.spot_handle,
                                                        self.dividend_yield,
                                                        self.flat_ts,
                                                        self.flat_vol_ts)
        binomial_engine = ql.BinomialVanillaEngine(self.bsm_process, "crr", self.steps)
        self.ql_option.setPricingEngine(binomial_engine)

    def estimate_vol_ql(self, targetValue: float, accuracy=1.0e-4, maxEvaluations=100, minVol=1.0e-4, maxVol=4.0):
        try:
            implied_vol = self.ql_option.impliedVolatility(targetValue, self.bsm_process, accuracy, maxEvaluations,
                                                               minVol, maxVol)
        except Exception as e:
            print(e)
            implied_vol = None
        return implied_vol

    def estimate_vol(self, price: float, presion: float = 0.00001,min_vol=0.01, max_vol: float = 2.0):
        l = min_vol
        r = max_vol
        while l < r and round((r - l), 5) > presion:
            m = round(l + (r - l) / 2, 5)
            self.reset_vol(m)
            p = self.NPV()
            if p < price:
                l = m
            else:
                r = m
        return m


class QlBlackFormula(AbstractOptionPricingEngine):
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
        self.dt_eval = dt_eval
        self.dt_maturity = dt_maturity
        self.option_type = option_type
        self.values: typing.List[typing.List[float]] = []
        self.asset_values: typing.List[typing.List[float]] = []
        self.exercise_values: typing.List[typing.List[float]] = []
        self.strike = strike
        self.spot = spot
        self.vol = vol
        self.rf = rf
        self.dividend_rate = dividend_rate
        self.maturity_date = constant.QuantlibUtil.to_ql_date(dt_maturity)
        self.settlement = constant.QuantlibUtil.to_ql_date(dt_eval)
        ql.Settings.instance().evaluationDate = self.settlement
        if option_type == constant.OptionType.PUT:
            self.ql_option_type = ql.Option.Put
        else:
            self.ql_option_type = ql.Option.Call
        payoff = ql.PlainVanillaPayoff(self.ql_option_type, strike)
        self.exercise = ql.EuropeanExercise(self.maturity_date)
        self.ql_option = ql.VanillaOption(payoff, self.exercise)
        self.day_count = ql.ActualActual()
        self.calendar = ql.China()
        self.spot_handle = ql.QuoteHandle(ql.SimpleQuote(spot))
        self.flat_ts = ql.YieldTermStructureHandle(
            ql.FlatForward(self.settlement, rf, self.day_count)
        )
        self.dividend_yield = ql.YieldTermStructureHandle(
            ql.FlatForward(self.settlement, self.dividend_rate, self.day_count)
        )
        self.flat_vol_ts = ql.BlackVolTermStructureHandle(
            ql.BlackConstantVol(self.settlement, self.calendar, self.vol, self.day_count)
        )
        self.bsm_process = ql.BlackScholesMertonProcess(self.spot_handle,
                                                        self.dividend_yield,
                                                        self.flat_ts,
                                                        self.flat_vol_ts)
        engine = ql.AnalyticEuropeanEngine(self.bsm_process)
        self.ql_option.setPricingEngine(engine)

    def NPV(self) -> float:
        return self.ql_option.NPV()

    def Delta(self,implied_vol:float=None) -> float:
        if implied_vol is not None: self.reset_vol(implied_vol)
        return self.ql_option.delta()

    def Gamma(self,implied_vol:float=None) -> float:
        if implied_vol is not None: self.reset_vol(implied_vol)
        return self.ql_option.gamma()

    def Theta(self,implied_vol:float=None) -> float:
        if implied_vol is not None: self.reset_vol(implied_vol)
        theta = self.ql_option.theta()/365.0
        return theta

    def Vega(self,implied_vol:float=None) -> float:
        if implied_vol is not None: self.reset_vol(implied_vol)
        vega = self.ql_option.vega()/100.0
        return vega

    def reset_vol(self, vol):
        self.vol = vol
        self.flat_vol_ts = ql.BlackVolTermStructureHandle(
            ql.BlackConstantVol(self.settlement, self.calendar, vol, self.day_count)
        )
        self.bsm_process = ql.BlackScholesMertonProcess(self.spot_handle,
                                                        self.dividend_yield,
                                                        self.flat_ts,
                                                        self.flat_vol_ts)
        engine = ql.AnalyticEuropeanEngine(self.bsm_process)
        self.ql_option.setPricingEngine(engine)

    def estimate_vol(self, price: float, presion: float = 0.00001, max_vol: float = 2.0):
        l = presion
        r = max_vol
        while l < r and round((r - l), 5) > presion:
            m = round(l + (r - l) / 2, 5)
            self.reset_vol(m)
            p = self.NPV()
            if p < price:
                l = m
            else:
                r = m
        return m

mdt = datetime.date.today() + datetime.timedelta(days=30)
p = QlBinomial(datetime.date.today(),mdt,constant.OptionType.PUT,constant.OptionExerciseType.EUROPEAN,
                   spot=2.5,strike=2.5)
implied_vol=p.estimate_vol(price=0.1)
p.reset_vol(implied_vol)
print(implied_vol)
print(p.NPV())
print(p.Delta())
print(p.Gamma())
print(p.Theta())
print(p.Vega())

mdt = datetime.date.today() + datetime.timedelta(days=30)
p = QlBlackFormula(datetime.date.today(),mdt,constant.OptionType.PUT,
                   spot=2.5,strike=2.5)
implied_vol=p.estimate_vol(price=0.1)
p.reset_vol(implied_vol)
print(implied_vol)
print(p.NPV())
print(p.Delta())
print(p.Gamma())
print(p.Theta())
print(p.Vega())
