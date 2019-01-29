import math
from scipy.stats import norm
from back_test.model.constant import OptionType
from back_test.model.constant_pricing import OptionType,PricingUtil

""" European Option Pricing and Metrics """


class BlackCalculator(object):

    def __init__(self,
                 ttm:float,
                 strike: float,
                 type: OptionType,
                 spot: float,
                 vol: float,
                 rf: float = 0.03):
        self.rf = rf
        self.vol = vol
        self.option_type = type
        if type == OptionType.CALL:
            self.iscall = True
        else:
            self.iscall = False
        discount = math.exp(-rf * ttm)
        self.ttm = ttm
        # self.dt_eval = dt_eval
        # self.dt_maturity = dt_maturity
        self.strike = strike
        self.forward = spot / discount
        self.discount = discount
        self.spot = spot
        stdDev = vol * math.sqrt(ttm)
        # stdDev = PricingUtil.get_std(dt_eval, dt_maturity, vol)
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

        if self.iscall:
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

    def NPV(self):
        return self.discount * (self.forward * self.alpha + self.x * self.beta)

    def Alpha(self):
        # Replicate portfolio -- component shares of stock,
        # N(d1) for call / -N(-d1) for put
        return self.alpha

    def Beta(self):
        # Replicate portfolio -- component shares of borrowing/lending,
        # -N(d2) for call / N(-d2) for put
        return self.beta

    def Cash(self):
        return self.beta * self.strike * self.discount

    def Delta(self):
        if self.spot <= 0.0:
            return
        elif self.ttm==0.0:
            if self.iscall:
                if self.strike < self.spot:
                    delta = 1.0
                elif self.strike > self.spot:
                    delta = 0.0
                else:
                    delta = 0.5
            else:
                if self.strike > self.spot:
                    delta = -1.0
                elif self.strike < self.spot:
                    delta = 0.0
                else:
                    delta = -0.5
        else:
            DforwardDs = self.forward / self.spot
            temp = self.stdDev * self.spot
            DalphaDs = self.dAlpha_dD1 / temp
            DbetaDs = self.dBeta_dD2 / temp
            temp2 = DalphaDs * self.forward + self.alpha * DforwardDs + DbetaDs * self.x \
                    + self.beta * self.dX_dS
            delta = self.discount * temp2
        return delta

    """ 
    Gamma计算基于标的价格变化的绝对量（而不是百分点），即Delta
    """
    def Gamma(self):
        spot = self.spot
        if spot <= 0.0:
            return
        if self.ttm == 0.0:
            return 0.0
        DforwardDs = self.forward / spot
        temp = self.stdDev * spot
        DalphaDs = self.dAlpha_dD1 / temp
        DbetaDs = self.dBeta_dD2 / temp
        D2alphaDs2 = -DalphaDs / spot * (1 + self.D1 / self.stdDev)
        D2betaDs2 = -DbetaDs / spot * (1 + self.D2 / self.stdDev)
        temp2 = D2alphaDs2 * self.forward + 2.0 * DalphaDs * DforwardDs + D2betaDs2 * self.x \
                + 2.0 * DbetaDs * self.dX_dS
        gamma = self.discount * temp2
        # gamma1 = self.dAlpha_dD1/self.spot/self.stdDev
        return gamma

    def Gamma_1pct(self):
        black1 = BlackCalculator(self.ttm,self.strike,self.option_type,self.spot*1.01,self.vol,self.rf)
        black2 = BlackCalculator(self.ttm,self.strike,self.option_type,self.spot*0.99,self.vol,self.rf)
        effective_gamma = (black1.Delta()-black2.Delta())/2
        return effective_gamma

###########Sythetic Option 2019-1-7#############
# dt_eval = datetime.date.today()
# mdt = datetime.date.today() + datetime.timedelta(days=50)
# k = 4376.44
# vol = 0.2536
# spot = 4288.3234
# call = BlackCalculator(datetime.date.today(),mdt,k,OptionType.CALL,spot,vol)
# print(call.Delta())
# print(call.Gamma())
# gamma = call.Gamma()
# rho = 0.01
# tao = PricingUtil.get_ttm(dt_eval, mdt)
# H = (1.5 * math.exp(-0.03*tao) * (1.0/1000.0) * spot * (gamma ** 2) / rho) ** (1 / 3)
# print(H)

#########Sythetic Option 2019-1-9#############
# dt_eval = datetime.date.today()
# mdt = datetime.date.today() + datetime.timedelta(days=50)
# tao = 40.0/252.0
# k = 1.05
# # vol = 0.251319
# vol = 0.253768
# spot = 1
# call = BlackCalculator(tao,k,OptionType.CALL,spot,vol)
# print('d1 : ',call.D1)
# print('Delta : ',call.Delta())
# print('Gamma : ',call.Gamma())
# gamma = call.Gamma()
# rho = 0.01
# tao = PricingUtil.get_ttm(dt_eval, mdt)
# H = (1.5 * math.exp(-0.03*tao) * (1.0/1000.0) * spot * (gamma ** 2) / rho) ** (1 / 3)
# print('H : ',H)

