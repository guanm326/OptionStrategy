import back_test.model.constant as c
from PricingLibrary.EngineQuantlib import QlBlackFormula
import math
import datetime
import numpy as np


def whalley_wilmott(eval_date, spot, gamma, dt_maturity, rho=0.01):
    fee = 1.0 / 1000.0
    ttm = c.PricingUtil.get_ttm(eval_date, dt_maturity)
    H = (1.5 * math.exp(-0.03 * ttm) * fee * spot * (gamma ** 2) / rho) ** (1 / 3)
    return H


strike = 1000.0  # 行权价
option_exercise_type = c.OptionExerciseType.EUROPEAN  # 行权方式
option_type = c.OptionType.CALL  # 期权类型
buy_write = c.BuyWrite.BUY  # 持仓头寸
vol = 0.2  # 波动率
rf = 0.03  # 利率
dt_eval = datetime.date(2018, 1, 6)  # 估值日
dt_maturity = dt_eval + datetime.timedelta(days=50)


spot = 1000.0  # 标的价格
black_formula = QlBlackFormula(dt_eval=dt_eval, dt_maturity=dt_maturity, option_type=option_type,
                               spot=spot, strike=strike, vol=vol, rf=rf)
delta = black_formula.Delta(vol)
last_delta = delta
last_spot = spot
res = []
print('ww model,spot从1000到2000调仓信息')
print('-'*100)
print("%20s %20s %20s"% ('spot', 'dS', 'gamma'))
print('-'*100)
for spot in np.arange(1000.0, 2000.0, 0.5):
    black_formula = QlBlackFormula(dt_eval=dt_eval, dt_maturity=dt_maturity, option_type=option_type,
                                   spot=spot, strike=strike, vol=vol, rf=rf)
    gamma = black_formula.Gamma(vol)
    delta = black_formula.Delta(vol)
    H = whalley_wilmott(dt_eval, spot, gamma, dt_maturity, rho=0.01)
    if abs(delta - last_delta) > H:
        print("%20s %20s %20s" % (spot, spot - last_spot, round(gamma,5)))

        res.append(spot - last_spot)
        last_spot = spot
        last_delta = delta
print('')

spot = 1000.0  # 标的价格
black_formula = QlBlackFormula(dt_eval=dt_eval, dt_maturity=dt_maturity, option_type=option_type,
                               spot=spot, strike=strike, vol=vol, rf=rf)
delta = black_formula.Delta(vol)
last_delta = delta
last_spot = spot
res = []
print('ww model,spot从1000到500调仓信息')
print('-'*100)
print("%20s %20s %20s"% ('spot', 'dS', 'gamma'))
print('-'*100)
for spot in np.arange(1000.0, 500.0, -0.5):
    black_formula = QlBlackFormula(dt_eval=dt_eval, dt_maturity=dt_maturity, option_type=option_type,
                                   spot=spot, strike=strike, vol=vol, rf=rf)
    gamma = black_formula.Gamma(vol)
    delta = black_formula.Delta(vol)
    H = whalley_wilmott(dt_eval, spot, gamma, dt_maturity, rho=0.01)
    if abs(delta - last_delta) > H:
        print("%20s %20s %20s" % (spot, spot - last_spot, round(gamma,5)))

        res.append(spot - last_spot)
        last_spot = spot
        last_delta = delta
print('')




spot = 1000.0  # 标的价格
black_formula = QlBlackFormula(dt_eval=dt_eval, dt_maturity=dt_maturity, option_type=option_type,
                               spot=spot, strike=strike, vol=vol, rf=rf)
delta = black_formula.Delta(vol)
last_delta = delta
last_spot = spot
print('fixed 0.1,spot从1000到2000调仓信息')
print('-'*100)
print("%20s %20s %20s"% ('spot', 'dS', 'gamma'))
print('-'*100)
for spot in np.arange(1000.0, 2000.0, 0.5):
    black_formula = QlBlackFormula(dt_eval=dt_eval, dt_maturity=dt_maturity, option_type=option_type,
                                   spot=spot, strike=strike, vol=vol, rf=rf)
    gamma = black_formula.Gamma(vol)
    delta = black_formula.Delta(vol)
    H = whalley_wilmott(dt_eval, spot, gamma, dt_maturity, rho=0.01)
    if abs(delta - last_delta) > 0.1:
        print("%20s %20s %20s" % (spot, spot - last_spot, round(gamma,5)))
        res.append(spot - last_spot)
        last_spot = spot
        last_delta = delta
        # print(res)

spot = 1000.0  # 标的价格
black_formula = QlBlackFormula(dt_eval=dt_eval, dt_maturity=dt_maturity, option_type=option_type,
                               spot=spot, strike=strike, vol=vol, rf=rf)
delta = black_formula.Delta(vol)
last_delta = delta
last_spot = spot
print('fixed 0.1,spot从1000到500调仓信息')
print('-'*100)
print("%20s %20s %20s"% ('spot', 'dS', 'gamma'))
print('-'*100)
for spot in np.arange(1000.0, 500.0, -0.5):
    black_formula = QlBlackFormula(dt_eval=dt_eval, dt_maturity=dt_maturity, option_type=option_type,
                                   spot=spot, strike=strike, vol=vol, rf=rf)
    gamma = black_formula.Gamma(vol)
    delta = black_formula.Delta(vol)
    H = whalley_wilmott(dt_eval, spot, gamma, dt_maturity, rho=0.01)
    if abs(delta - last_delta) > 0.1:
        print("%20s %20s %20s" % (spot, spot - last_spot, round(gamma,5)))
        res.append(spot - last_spot)
        last_spot = spot
        last_delta = delta
        # print(res)
