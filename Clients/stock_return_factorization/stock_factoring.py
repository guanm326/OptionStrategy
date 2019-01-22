import datetime

import matplotlib.pyplot as plt
import pandas as pd
import statsmodels.api as sm

from Utilities.PlotUtil import PlotUtil
from back_test.model.constant import HistoricalVolatility as hv

pu = PlotUtil()
data = pd.read_excel('data/sw2_indexes.xlsx')
col_names = list(data.columns)
col_names.remove('date')
col_names.remove('000300.SH')
col_names.remove('000905.SH')
col_names.remove('000016.SH')

data['BETA'] = hv.arithmetic_yield(data['000300.SH'])
data['r_index50'] = hv.arithmetic_yield(data['000016.SH'])
data['r_index500'] = hv.arithmetic_yield(data['000905.SH'])
data['SMB'] = data['r_index500'] - data['r_index50']
data = data.dropna(subset=['SMB','BETA']).set_index('date')

# 残差结果输出：BETA/SMB因子累计收益率
df_res = pd.DataFrame(index=data.index)
df_res['cum_beta'] = (1+data['BETA']).cumprod()
df_res['cum_smb'] = (1+data['SMB']).cumprod()

for col in col_names:
# col = col_names[1]
    data['y_index'] = hv.arithmetic_yield(data[col])
    data_reg = data[['y_index', 'BETA', 'SMB']].copy().dropna()
    ols = sm.OLS(data_reg['y_index'], data_reg[['BETA', 'SMB']]).fit()
    rsd = ols.resid
    df_res['cum_rsd_'+col] = (1+rsd).cumprod()

df_res.to_csv('data/results_stock_factoring.csv')