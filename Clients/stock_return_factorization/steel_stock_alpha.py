import matplotlib.pyplot as plt
import pandas as pd
import datetime
import statsmodels.api as sm
from Utilities.PlotUtil import PlotUtil
from back_test.model.constant import HistoricalVolatility as hv
from back_test.model.constant import Statistics

def flag_t_test(pvalues):
    for p in pvalues:
        if p>0.01:
            return False
    return True

def top_index(cols,data):
    df_top = data.copy()
    df_top = df_top[cols]
    series = df_top.mean(axis=1)
    return series


data_1 = pd.read_excel('data/steel_mktdata.xlsx')
data_2 = pd.read_excel('data/steel_industry_data.xlsx', sheetname='data')
data_3 = pd.read_excel('data/sw_steel_closes.xlsx')
data = data_1.join(data_2.set_index('date'), on='date', how='left')
data = data.join(data_3.set_index('date'), on='date', how='left')
col_names = list(data_3.columns)
col_names.remove('date')
col_names.append('steel_index_bysales')
col_names.append('801041.SI')
top_five = ['000932.SZ','002110.SZ','600507.SH','601003.SH','000717.SZ']
top_ten = ['000932.SZ','002110.SZ','600507.SH','601003.SH','000717.SZ',
           '600282.SH','600808.SH','000825.SZ','600569.SH','000959.SZ']

index_top5 = top_index(top_five,data)
data['index_top5'] = index_top5

index_top10 = top_index(top_ten,data)
data['index_top10'] = index_top10

reg_start = datetime.date(2014, 3, 24)
data = data[data['date'] >= reg_start].reset_index(drop=True)
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

data_reg = data_reg[['y', 'BETA_S', 'SMB_S', 'HC_F']].dropna()
x_s = data_reg[['BETA_S', 'SMB_S', 'HC_F']]
y = data_reg['y']
reg = Statistics.linear_regression(x_s, y)
print(reg.params)
print(reg.pvalues)
print(reg.rsquared)
print(reg.rsquared_adj)
rsd = reg.resid
cum_rsd= (1+rsd).cumprod()
dates = list(data_reg.index)

df_cum_yield = pd.DataFrame(index=data.index)
for col in top_five:
    r = hv.arithmetic_yield(data[col])
    df_cum_yield[col] = (1 + r).cumprod()
df_cum_yield['BETA'] = (1+data['BETA_S']).cumprod()
df_cum_yield['cum_rsd_index_t5'] = cum_rsd
df_cum_yield.to_csv('data/top5_yield.csv')
pu.plot_line_chart(dates,[cum_rsd],['cum_rsd_top5_index'])

plt.show()
