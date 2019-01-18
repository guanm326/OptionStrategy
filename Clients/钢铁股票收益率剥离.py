import statsmodels.api as sm
import pandas as pd
from back_test.model.constant import HistoricalVolatility as hv
from Utilities.PlotUtil import PlotUtil
import matplotlib.pyplot as plt
import numpy as np

#y: pd.Series
#x: pd.DataFrame
# 600019.SH	000300.SH	IF.CFE	IH.CFE	IC.CFE

pu = PlotUtil()
data = pd.read_excel("钢铁股票收益率剥离.xlsx")
data['r_y'] = hv.log_yield(data['600019.SH'],20)
data['r_y_1'] = hv.arithmetic_yield(data['600019.SH'],20)
data['r_beta'] = hv.log_yield(data['000300.SH'])
data['r_if'] = hv.log_yield(data['IF.CFE'])
data['r_ih'] = hv.log_yield(data['IH.CFE'])
data['r_ic'] = hv.log_yield(data['IC.CFE'])
data['r_small'] = data['r_ic'] - data['r_ih']
data['r_rb'] = hv.log_yield(data['RB.SHF'])
data['r_earning'] = hv.log_yield(data['PRODCT_EARNING'])
# 一阶差分
data['d_y'] = np.log(data['600019.SH']).diff()
data['d_beta'] = np.log(data['000300.SH']).diff()
data['d_if'] = np.log(data['IF.CFE']).diff()
data['d_ih'] = np.log(data['IH.CFE']).diff()
data['d_ic'] = np.log(data['IC.CFE']).diff()
data['d_small'] = data['d_ic'] - data['d_ih']
data['d_rb'] = np.log(data['RB.SHF']).diff()
data['d_earning'] = np.log(data['PRODCT_EARNING']).diff()

data = data.dropna().reset_index(drop=True)
ols=sm.OLS(data['r_y'], sm.add_constant(data[['r_beta','r_small','d_rb','d_earning']])).fit()
rsd = ols.resid
cum_rsd = (1+rsd).cumprod().plot()
print(cum_rsd)
pu.plot_line_chart(list(data['Date']),[list(rsd)])
# pu.plot_line_chart(list(data['Date']),[list(cum_rsd)])
plt.show()