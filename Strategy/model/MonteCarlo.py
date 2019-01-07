import math
import matplotlib.pyplot as plt
import numpy as np
import back_test.model.constant as c
import pandas as pd
import datetime
from Utilities.PlotUtil import PlotUtil
np.random.seed(0)
df_base = pd.read_excel('../../../data/中证全指日收盘价.xlsx')
df_base[c.Util.DT_DATE] = df_base['日期'].apply(lambda x: x.date())
df_base = df_base.rename(columns={'000985.CSI': c.Util.AMT_CLOSE})
id_instrument = '000985.CSI'
df_base[c.Util.ID_INSTRUMENT] = id_instrument

# dt_start = datetime.date(2007,12,28)
dt_start = datetime.date(2006,12,29)
# dt_end = datetime.date(2008,12,31)
dt_end = datetime.date(2007,12,31)
data = df_base[(df_base[c.Util.DT_DATE] >= dt_start)&(df_base[c.Util.DT_DATE] <= dt_end)]
S0 = df_base[df_base[c.Util.DT_DATE] <= dt_start][c.Util.AMT_CLOSE].values[-1]# 2006年收盘价
T = len(data)-1
# mu = c.HistoricalVolatility.hist_yield_daily(data[c.Util.AMT_CLOSE],n=T).values[-1]

mu = math.log(data[c.Util.AMT_CLOSE].values[-1]/data[c.Util.AMT_CLOSE].values[0])/T # 几何平均
# mu = (data[c.Util.AMT_CLOSE].values[-1]-data[c.Util.AMT_CLOSE].values[0])/data[c.Util.AMT_CLOSE].values[0]/T # 算术平均
vol = c.HistoricalVolatility.hist_vol_daily(data[c.Util.AMT_CLOSE],n=T).values[-1]
# print(S0,T,mu,vol)
print('S0 ; ', data[c.Util.AMT_CLOSE].values[0])
print('ST  ', data[c.Util.AMT_CLOSE].values[-1])
print('log annual yield : ', math.log(data[c.Util.AMT_CLOSE].values[-1]/data[c.Util.AMT_CLOSE].values[0]))
print('annual yield : ', (data[c.Util.AMT_CLOSE].values[-1]-data[c.Util.AMT_CLOSE].values[0])/data[c.Util.AMT_CLOSE].values[0])
print('annual vol : ', vol*math.sqrt(T))
# print(data)
df_simulation = pd.DataFrame()
simulations = []
ST = []
i = 0
while i < 10000:
    daily_returns = np.random.normal(mu, vol, T)
    price_list = [S0]
    for r in daily_returns:
        # price_list.append(price_list[-1] * (1+r))
        price_list.append(price_list[-1] * math.exp(r))
    simulations.append(price_list)
    df_simulation['amt_close_'+str(i)] = price_list
    ST.append(price_list[-1])
    i += 1
print('Mean Simulated ST : ', sum(ST)/len(ST))
df_simulation[c.Util.DT_DATE] = list(data[c.Util.DT_DATE])
# df_simulation.to_csv('../../accounts_data/df_simulation.csv')
# pu = PlotUtil()
# dates = list(data[c.Util.DT_DATE])
# closes = list(data[c.Util.AMT_CLOSE])
# pu.plot_line_chart(dates,simulations)
# pu.plot_line_chart(dates,[closes])
# pu.plot_line_chart(np.arange(0,1000,1),[ST])
# # plt.show()
# plt.figure()
# plt.hist(ST, bins=100, density=True, facecolor="#CC0000", label="Simulated Terminal Price")
#
# plt.show()