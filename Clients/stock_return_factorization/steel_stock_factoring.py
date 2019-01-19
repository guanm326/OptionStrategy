import statsmodels.api as sm
import pandas as pd
from back_test.model.constant import HistoricalVolatility as hv
from Utilities.PlotUtil import PlotUtil
import matplotlib.pyplot as plt
import numpy as np
import datetime

pu = PlotUtil()
data = pd.read_excel('data/steel_mktdata.xlsx', dtype={'date': datetime.date})
data['y_600019'] = hv.log_yield(data['600019.SH'])
data['y_index'] = hv.log_yield(data['steel_index_bysales'])
data['BETA'] = hv.log_yield(data['000300.SH'])
data['r_index50'] = hv.log_yield(data['000016.SH'])
data['r_index500'] = hv.log_yield(data['000905.SH'])
data['SMB'] = data['r_index500'] - data['r_index50']
# data['r_ih'] = hv.log_yield(data['IH.CFE'])
# data['r_ic'] = hv.log_yield(data['IC.CFE'])
# data['r_small1'] = data['r_ic'] - data['r_ih']
# 一阶差分
data['DELTA_RB'] = np.log(data['RB.SHF']).diff()
data['DELTA_RB_PROFIT'] = np.log(data['steel_profit']).diff()

data = data[['date', 'y_index', 'BETA', 'SMB', 'DELTA_RB', 'DELTA_RB_PROFIT']].dropna().reset_index(drop=True)
# ols=sm.OLS(data['r_y_index'], sm.add_constant(data[['r_beta','r_small_index','d_rb','d_profit']])).fit()
ols = sm.OLS(data['y_index'], data[['BETA', 'SMB', 'DELTA_RB', 'DELTA_RB_PROFIT']]).fit()
rsd = ols.resid
cum_rsd = (1 + rsd).cumprod()
print('-'*50)
print('params')
print(ols.params)
print('-' * 50)

print('pvalues')
print(ols.pvalues)
print('-' * 50)
print('rsquared')
print(ols.rsquared)
print('-' * 50)

pu.plot_line_chart(list(data['date']), [list(rsd)])
pu.plot_line_chart(list(data['date']), [list(cum_rsd)])
plt.show()
