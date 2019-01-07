import math
import datetime
from PricingLibrary.BlackFormular import BlackFormula
from PricingLibrary.EngineQuantlib import QlBlackFormula
from PricingLibrary.BlackCalculator import BlackCalculator
import back_test.model.constant as c
import numpy as np
from Utilities.PlotUtil import PlotUtil
import matplotlib.pyplot as plt



pu = PlotUtil()
dt_eval = datetime.date(2017, 1, 1)
dt_maturity = datetime.date(2017, 4, 1)

strike = 51000 # 行权价
option_exercise_type = c.OptionExerciseType.EUROPEAN # 行权方式
option_type = c.OptionType.CALL # 期权类型
buy_write = c.BuyWrite.BUY # 持仓头寸
spot = 50000 # 标的价格
vol = 0.2 # 波动率
rf = 0.03 # 利率

# 行权方式为欧式期权、定价模型为BS进而选择QlBlackFormula

deltas = []
spots = []
for i in np.arange(0.6,1.6,0.05):
    s = spot*i
    black_formula = QlBlackFormula(dt_eval=dt_eval, dt_maturity=dt_maturity, option_type=option_type,
                                   spot=s, strike=strike, vol=vol, rf=rf)
    delta = black_formula.Delta(vol)
    spots.append(s)
    deltas.append(delta)

pu.plot_line_chart(np.arange(0.6,1.6,0.05),[deltas],['delta'])

plt.show()