import matplotlib.pyplot as plt
import pandas as pd
import statsmodels.api as sm
from Utilities.PlotUtil import PlotUtil
from back_test.model.constant import HistoricalVolatility as hv

pu = PlotUtil()
data_1 = pd.read_excel('data/steel_mktdata.xlsx')
data_2 = pd.read_excel('data/steel_industry_data.xlsx',sheetname='data')
data = data_1.join(data_2.set_index('date'), on='date', how='left')
data['y_600019'] = hv.arithmetic_yield(data['600019.SH'])
# data['y_index'] = hv.arithmetic_yield(data['801041.SI'])
# data['y_index'] = hv.arithmetic_yield(data['steel_index_bysales'])
data['BETA'] = hv.arithmetic_yield(data['000300.SH'])
data['r_index50'] = hv.arithmetic_yield(data['000016.SH'])
data['r_index500'] = hv.arithmetic_yield(data['000905.SH'])
data['SMB'] = data['r_index500'] - data['r_index50']
data['RB_PRICE'] = hv.arithmetic_yield(data['RB.SHF'])
data['HC_PRICE'] = hv.arithmetic_yield(data['HC.SHF'])
data['I_PRICE'] = hv.arithmetic_yield(data['I.DCE'])
data['J_PRICE'] = hv.arithmetic_yield(data['J.DCE'])
data['LC_PRICE'] = hv.arithmetic_yield(data['LC'])
data['GC_PRICE'] = hv.arithmetic_yield(data['GC'])
data['RB_PROFIT'] = hv.arithmetic_yield(data['steel_profit']) # 期货

data_reg = data[['date', 'y_600019', 'BETA', 'SMB']].dropna().reset_index(drop=True)
ols = sm.OLS(data_reg['y_600019'], data_reg[['BETA']]).fit()
rsd = ols.resid
data_reg['rsd'] = rsd
cum_rsd = (1+rsd).cumprod()
cum_steel_index = (1+data_reg['y_600019']).cumprod()
cum_beta = (1+data_reg['BETA']).cumprod()
cum_smb = (1+data_reg['SMB']).cumprod()
# cum_rb = (1+data_reg['RB_PRICE']).cumprod()
# cum_hc = (1+data_reg['HC_PRICE']).cumprod()
# cum_lc = (1+data_reg['LC_PRICE']).cumprod()
# cum_rb_profit = (1+data_reg['RB_PROFIT']).cumprod()
data_reg['cum_rsd'] = cum_rsd
# data_reg['cum_y_600019'] = cum_steel_index
# data_reg['cum_beta'] = cum_beta
# data_reg['cum_smb'] = cum_smb
# data_reg['cum_rb'] = cum_rb
# data_reg['cum_rb_profit'] = cum_rb_profit
data_reg.to_csv('data/regress_result.csv')
print('-' * 50)
print('params')
print(ols.params)
print('-' * 50)
print('pvalues')
print(ols.pvalues)
print('-' * 50)
print('rsquared')
print(ols.rsquared)
print('-' * 50)

# pu.plot_line_chart(list(data_reg['date']), [list(cum_rsd),list(cum_lc),
#                                             list(cum_rb), list(cum_hc),list(cum_rb_profit)],
#                    ['cum_rsd','cum_lc', 'cum_rb', 'cum_hc','cum_rb_profit'])
# plt.show()
