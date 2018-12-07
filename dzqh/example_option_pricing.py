from dzqh.EngineQuantlib import QlBlackFormula,QlBinomial,QlBAW
import dzqh.constant as c
import datetime
from dzqh.PlotUtil import PlotUtil
import numpy as np
import matplotlib.pyplot as plt


pu = PlotUtil()

# 1. 期权估值
# 参数输入
strike = 51000 # 行权价
option_exercise_type = c.OptionExerciseType.EUROPEAN # 行权方式
option_type = c.OptionType.CALL # 期权类型
dt_maturity = datetime.date(2018,12,25) # 到期日
buy_write = c.BuyWrite.BUY # 持仓头寸
spot = 50000 # 标的价格
vol = 0.2 # 波动率
rf = 0.03 # 利率
dt_eval = datetime.date(2018,12,6) # 估值日

# 行权方式为欧式期权、定价模型为BS进而选择QlBlackFormula
black_formula = QlBlackFormula(dt_eval=dt_eval,dt_maturity=dt_maturity,option_type=option_type,
                   spot=spot,strike=strike,vol=vol,rf=rf)
print('option price BS : ',black_formula.NPV())
print('vol BS : ',vol)
print('delta BS : ',black_formula.Delta())
print('gamma BS : ',black_formula.Gamma())
print('Theta BS : ',black_formula.Theta())
print('Vega BS : ',black_formula.Vega())


# 2. 隐含波动率计算
# 参数输入
strike = 51000 # 行权价
option_type = c.OptionType.CALL # 期权类型
dt_maturity = datetime.date(2018,12,25) # 到期日
buy_write = c.BuyWrite.BUY# 持仓头寸
spot = 50000 # 标的价格
rf = 0.03 # 利率
dt_eval = datetime.date(2018,12,6) # 估值日
option_price = 531

# 行权方式为欧式期权、定价模型为BS进而选择QlBlackFormula
black_formula = QlBlackFormula(dt_eval=dt_eval,dt_maturity=dt_maturity,option_type=option_type,
                   spot=spot,strike=strike,rf=rf)
vol = black_formula.estimate_vol(option_price)
print('option price BS : ',black_formula.NPV())
print('vol BS : ',vol)
print('delta BS : ',black_formula.Delta(vol))
print('gamma BS : ',black_formula.Gamma(vol))
print('Theta BS : ',black_formula.Theta())
print('Vega BS : ',black_formula.Vega())


# 3.Plot Graphs
min_k = strike*0.8
max_k = strike*1.2
strikes = np.arange(min_k,max_k,(max_k-min_k)/1000.0)
deltas = []
gammas = []
thetas = []
vegas = []
for k in strikes:
    black_formula = QlBlackFormula(dt_eval=dt_eval,dt_maturity=dt_maturity,option_type=option_type,
                   spot=spot,strike=k,vol=vol,rf=rf)
    delta = black_formula.Delta(vol)*buy_write.value
    gamma = black_formula.Gamma(vol)*buy_write.value
    theta = black_formula.Theta()
    vaga = black_formula.Vega()
    deltas.append(delta)
    gammas.append(gamma)
    thetas.append(theta)
    vegas.append(vaga)

pu.plot_line_chart(strikes,[deltas],['delta'])
pu.plot_line_chart(strikes,[gammas],['gamma'])
pu.plot_line_chart(strikes,[thetas],['theta'])
pu.plot_line_chart(strikes,[vegas],['vega'])

plt.show()



