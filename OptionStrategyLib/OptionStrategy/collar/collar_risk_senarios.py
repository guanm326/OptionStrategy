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
dt_eval = datetime.date(2018,9,20)
dt_maturity = datetime.date(2019,1,16)
spot = 70 # 标的价格
vol = 0.3 # 波动率

# # Buy Call @70
# call1 = QlBlackFormula(dt_eval=dt_eval,dt_maturity=dt_maturity,option_type=c.OptionType.CALL,
#                    spot=spot,strike=75,vol=vol,rf=0.03)
# call_price_70 = 3.65
# call_price_75 = 1.75
# iv_call = call1.estimate_vol(call_price_75)
# print('vol call 70 : ',iv_call)
#
# # Sell Put @60
# put1 = QlBlackFormula(dt_eval=dt_eval,dt_maturity=dt_maturity,option_type=c.OptionType.PUT,
#                    spot=spot,strike=65,vol=vol,rf=0.03)
# put_price_60 = 0.87
# put_price_65 = 2.01
# iv_put = put1.estimate_vol(put_price_65)
# print('vol put 60 : ',iv_put)

ps=[]

for eval in [datetime.date(2018,10,15),datetime.date(2018,12,15),datetime.date(2019,1,15)]:
    p = []
    for spot in np.arange(40.0,100.0,1.0):
        call = QlBinomial(dt_eval=eval, dt_maturity=dt_maturity, option_type=c.OptionType.CALL,option_exercise_type=c.OptionExerciseType.AMERICAN,
                                 spot=spot, strike=75, vol=vol, rf=0.03)
        put = QlBinomial(dt_eval=eval, dt_maturity=dt_maturity, option_type=c.OptionType.PUT,option_exercise_type=c.OptionExerciseType.AMERICAN,
                                spot=spot, strike=65, vol=vol, rf=0.03)
        short = 70-spot
        # print(call.NPV())
        # print(put.NPV())
        # print(short)
        if call.NPV()-put.NPV()+short < 0.0: print(spot)
        p.append(1000*(call.NPV()-put.NPV()+short))
        # p.append(call.NPV()-put.NPV()+short)
    ps.append(p)

pu.plot_line_chart(np.arange(40,100,1), ps,['T=3M 收益结构','T=1M 收益结构','到期收益结构'])
ps=[]
for v in [0.3,0.5,0.7]:
    p = []
    for spot in np.arange(40.0,100.0,1.0):
        call = QlBinomial(dt_eval=datetime.date(2018,11,15), dt_maturity=dt_maturity, option_type=c.OptionType.CALL,option_exercise_type=c.OptionExerciseType.AMERICAN,
                                 spot=spot, strike=75, vol=v, rf=0.03)
        put = QlBinomial(dt_eval=datetime.date(2018,11,15), dt_maturity=dt_maturity, option_type=c.OptionType.PUT,option_exercise_type=c.OptionExerciseType.AMERICAN,
                                spot=spot, strike=65, vol=v, rf=0.03)
        short = 70-spot
        # print(call.NPV())
        # print(put.NPV())
        # print(short)
        if call.NPV()-put.NPV()+short < 0.0: print(spot)
        p.append(1000*(call.NPV()-put.NPV()+short))
        # p.append(call.NPV()-put.NPV()+short)
    ps.append(p)

pu.plot_line_chart(np.arange(40,100,1), ps,['波动率30%，T=2M','波动率50%，T=2M','波动率70%，T=2M'])


ps=[]

for eval in [datetime.date(2018,10,15),datetime.date(2018,12,15),datetime.date(2019,1,15)]:
    p = []
    for spot in np.arange(40.0,100.0,1.0):
        call = QlBinomial(dt_eval=eval, dt_maturity=dt_maturity, option_type=c.OptionType.CALL,option_exercise_type=c.OptionExerciseType.AMERICAN,
                                 spot=spot, strike=70, vol=vol, rf=0.03)
        put = QlBinomial(dt_eval=eval, dt_maturity=dt_maturity, option_type=c.OptionType.PUT,option_exercise_type=c.OptionExerciseType.AMERICAN,
                                spot=spot, strike=60, vol=vol, rf=0.03)
        short = 70-spot
        # print(call.NPV())
        # print(put.NPV())
        # print(short)
        if call.NPV()-put.NPV()+short < 0.0: print(spot)
        p.append(1000*(call.NPV()-4*put.NPV()+short))
        # p.append(call.NPV()-put.NPV()+short)
    ps.append(p)

pu.plot_line_chart(np.arange(40,100,1), ps,['T=3M 收益结构','T=1M 收益结构','到期收益结构'])
ps=[]
for v in [0.3,0.5,0.7]:
    p = []
    for spot in np.arange(40.0,100.0,1.0):
        call = QlBinomial(dt_eval=datetime.date(2018,11,15), dt_maturity=dt_maturity, option_type=c.OptionType.CALL,option_exercise_type=c.OptionExerciseType.AMERICAN,
                                 spot=spot, strike=70, vol=v, rf=0.03)
        put = QlBinomial(dt_eval=datetime.date(2018,11,15), dt_maturity=dt_maturity, option_type=c.OptionType.PUT,option_exercise_type=c.OptionExerciseType.AMERICAN,
                                spot=spot, strike=60, vol=v, rf=0.03)
        short = 70-spot
        # print(call.NPV())
        # print(put.NPV())
        # print(short)
        if call.NPV()-put.NPV()+short < 0.0: print(spot)
        p.append(1000*(call.NPV()-4*put.NPV()+short))
        # p.append(call.NPV()-put.NPV()+short)
    ps.append(p)

pu.plot_line_chart(np.arange(40,100,1), ps,['波动率30%，T=2M','波动率50%，T=2M','波动率70%，T=2M'])
plt.show()

# mu_day = 0.15/252.0
# sigma_day = 0.3/math.sqrt(252)
# T =int(252/3)
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
# nbr = len(df_ST[df_ST['ST']>=60])
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
