from dzqh.EngineQuantlib import QlBlackFormula,QlBinomial,QlBAW
import dzqh.constant as c
import datetime
from Utilities.PlotUtil import PlotUtil
import numpy as np
import matplotlib.pyplot as plt
import math
import pandas as pd


pu = PlotUtil()

# 1. 浅虚值看跌
dt_eval = datetime.date.today()
dt_maturity = dt_eval + datetime.timedelta(days=int(365/4)) # 到期日
spot = 70.0 # 标的价格
vol = 0.3 # 波动率

# Buy Call
call = QlBlackFormula(dt_eval=dt_eval,dt_maturity=dt_maturity,option_type=c.OptionType.CALL,
                   spot=spot,strike=80,vol=vol,rf=0.03)
print('call : ',call.NPV())
# print('vol BS : ',vol)
# print('delta BS : ',call.Delta())
# print('gamma BS : ',call.Gamma())
# print('Theta BS : ',call.Theta())
# print('Vega BS : ',call.Vega())

put = QlBlackFormula(dt_eval=dt_eval,dt_maturity=dt_maturity,option_type=c.OptionType.PUT,
                   spot=spot,strike=63,vol=vol,rf=0.03)
print('put1 : ',put.NPV())
# print('vol BS : ',vol)
# print('delta BS : ',put.Delta())
# print('gamma BS : ',put.Gamma())
# print('Theta BS : ',put.Theta())
# print('Vega BS : ',put.Vega())

put1 = QlBlackFormula(dt_eval=dt_eval,dt_maturity=dt_maturity,option_type=c.OptionType.PUT,
                   spot=spot,strike=50,vol=vol,rf=0.03)
print('put2 : ',put1.NPV())
# print('vol BS : ',vol)
# print('delta BS : ',put1.Delta())
# print('gamma BS : ',put1.Gamma())
# print('Theta BS : ',put1.Theta())
# print('Vega BS : ',put1.Vega())



# mu_day = 0/252.0
# sigma_day = 0.3/math.sqrt(252)
# T =int(252/4)
# S0 = 70
# simulations = []
# ST = []
# i = 0
# while i < 1000:
#     daily_returns = np.random.normal(mu_day, sigma_day, T)
#     price_list = [S0]
#     for r in daily_returns:
#         # price_list.append(price_list[-1] * (1+r))
#         price_list.append(price_list[-1] * math.exp(r))
#     simulations.append(price_list)
#     ST.append(price_list[-1])
#     i += 1
# print('Mean Simulated ST : ', sum(ST)/len(ST))
# df_ST = pd.DataFrame({'ST':ST})
# nbr = len(df_ST[df_ST['ST']>=50])
# print(nbr/len(df_ST))
# pu.plot_line_chart(np.arange(T+1),simulations)
# plt.figure()
# plt.hist(ST, bins=100, density=True, facecolor="#CC0000", label="Simulated Terminal Price")
# plt.show()



# # 3.Plot Graphs
# min_k = strike*0.8
# max_k = strike*1.2
# strikes = np.arange(min_k,max_k,(max_k-min_k)/1000.0)
# deltas = []
# gammas = []
# thetas = []
# vegas = []
# for k in strikes:
#     black_formula = QlBlackFormula(dt_eval=dt_eval,dt_maturity=dt_maturity,option_type=option_type,
#                    spot=spot,strike=k,vol=vol,rf=rf)
#     delta = black_formula.Delta(vol)*buy_write.value
#     gamma = black_formula.Gamma(vol)*buy_write.value
#     theta = black_formula.Theta()
#     vaga = black_formula.Vega()
#     deltas.append(delta)
#     gammas.append(gamma)
#     thetas.append(theta)
#     vegas.append(vaga)
#
# pu.plot_line_chart(strikes,[deltas],['delta'])
# pu.plot_line_chart(strikes,[gammas],['gamma'])
# pu.plot_line_chart(strikes,[thetas],['theta'])
# pu.plot_line_chart(strikes,[vegas],['vega'])
#
# plt.show()
#
#
#
