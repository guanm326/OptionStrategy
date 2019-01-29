import matplotlib.pyplot as plt
import pandas as pd
import datetime
import statsmodels.api as sm
from Utilities.PlotUtil import PlotUtil
from back_test.model.constant import HistoricalVolatility as hv
from back_test.model.constant import Statistics, Util
from back_test.model.base_account import BaseAccount
import numpy as np

def flag_t_test(pvalues):
    for p in pvalues:
        if p > 0.01:
            return False
    return True


def top_index(cols, data):
    df_top = data.copy()
    df_top = df_top[cols]
    series = df_top.mean(axis=1)
    return series


data_1 = pd.read_excel('data/steel_mktdata_AdjF.xlsx')
data_2 = pd.read_excel('data/steel_industry_data.xlsx', sheetname='data')
data_3 = pd.read_excel('data/sw_steel_closes_AdjF.xlsx')
data = data_1.join(data_2.set_index('date'), on='date', how='left')
data = data.join(data_3.set_index('date'), on='date', how='left')
col_names = list(data_3.columns)
col_names.remove('date')
col_names.append('steel_index_bysales')
col_names.append('801041.SI')
# top_five = ['600507.SH','002110.SZ','601003.SH','000932.SZ','600782.SH']
top_five = ['600231.SH','600507.SH','000932.SZ','600782.SH','000717.SZ']

index_top5 = top_index(top_five, data)
data['index_top5'] = index_top5

reg_start = datetime.date(2018, 1, 1)
# reg_end = datetime.date(2017,12,31)
reg_end = datetime.date.today()
data = data[(data['date'] >= reg_start)&(data['date'] <= reg_end)].reset_index(drop=True)
data['BETA_F'] = hv.arithmetic_yield(data['IF.CFE'])
data['BETA_S'] = hv.arithmetic_yield(data['000300.SH'])
data['SMB_F'] = hv.arithmetic_yield(data['IC.CFE']) - hv.arithmetic_yield(data['IH.CFE'])
data['SMB_S'] = hv.arithmetic_yield(data['000905.SH']) - hv.arithmetic_yield(data['000016.SH'])
data['RB_F'] = hv.arithmetic_yield(data['RB.SHF'])
data['RB_S'] = hv.arithmetic_yield(data['RB'])
data['HC_F'] = hv.arithmetic_yield(data['HC.SHF'])
data['HC_S'] = hv.arithmetic_yield(data['HC'])
data['I_F'] = hv.arithmetic_yield(data['I.DCE'])
data['J_F'] = hv.arithmetic_yield(data['J.DCE'])
data['LC_S'] = hv.arithmetic_yield(data['LC'])
data['GC_S'] = hv.arithmetic_yield(data['GC'])
data['RB_PROFIT_F'] = hv.arithmetic_yield(data['steel_profit'])  # 期货
data = data.set_index('date')

pu = PlotUtil()

data_reg = data.copy()
data_reg['y'] = hv.arithmetic_yield(data_reg['index_top5'])

data_reg = data_reg[['y', 'BETA_F', 'SMB_F', 'HC_F']].dropna()
x_s = data_reg[['BETA_F', 'SMB_F', 'HC_F']]
y = data_reg['y']
reg = Statistics.linear_regression(x_s, y)
print(reg.params)
print(reg.pvalues)
print(reg.rsquared)
print(reg.rsquared_adj)

# a_beta = reg.params['BETA_F']
# a_smb = reg.params['SMB_F']
# a_hc = reg.params['HC_F']

a_beta = 0.744710
a_smb = 0.399662
a_hc = 0.244484
init_stock = Util.BILLION / 100

data_hedge = data.iloc[1:,:].copy()
# data_hedge = data_hedge[['index_top5', '000300.SH', '000905.SH', '000016.SH', 'HC.SHF']]
data_hedge = data_hedge[['index_top5', 'IF.CFE', 'IC.CFE', 'IH.CFE', 'HC.SHF']]
init_closes = np.array(data_hedge.iloc[0])
weights = np.array([1, -a_beta, -a_smb, a_smb, -a_hc])
init_mktvalues = weights*init_stock
init_capital = sum(np.array([1, a_beta*0.2, a_smb*0.2, a_smb*0.2, a_hc*0.2])*init_stock) # 五倍杠杆
units = init_mktvalues/init_closes
print(units)
print(np.array(data_hedge.iloc[0]))
print(np.array(data_hedge.iloc[1]))
data_hedge['hedged_mkv'] = data_hedge.apply(lambda x:sum(x*units),axis=1)
data_hedge['pnl'] = data_hedge['hedged_mkv'] -data_hedge.iloc[0]['hedged_mkv']
data_hedge['NPV'] = (data_hedge['pnl']+init_capital)/init_capital

account = BaseAccount(init_capital,rf=0.0)
res = account.get_netvalue_analysis(data_hedge['NPV'])
print(res)
data_hedge.to_csv('data/result_hedged_port.csv')
