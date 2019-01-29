import matplotlib.pyplot as plt
import pandas as pd
import datetime
import statsmodels.api as sm
from Utilities.PlotUtil import PlotUtil
from back_test.model.constant import HistoricalVolatility as hv
from back_test.model.constant import Regression

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


data_1 = pd.read_excel('data/steel_mktdata_AdjF.xlsx')
data_2 = pd.read_excel('data/steel_industry_data.xlsx', sheetname='data')
data_3 = pd.read_excel('data/sw_steel_closes_AdjF.xlsx')
data = data_1.join(data_2.set_index('date'), on='date', how='left')
data = data.join(data_3.set_index('date'), on='date', how='left')
col_names = list(data_3.columns)
col_names.remove('date')
col_names.append('steel_index_bysales')
col_names.append('801041.SI')
top_five = ['600507.SH','002110.SZ','601003.SH','000932.SZ','600782.SH']


index_top5 = top_index(top_five,data)
data['index_top5'] = index_top5

reg_start = datetime.date(2005, 1, 1)
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
data_reg['y'] = hv.arithmetic_yield(data_reg['steel_index_bysales'])
# data_reg['y'] = hv.arithmetic_yield(data_reg['801041.SI'])

data_reg = data_reg[['y', 'BETA_S', 'SMB_S', 'HC_S']].dropna()
x_s = data_reg[['BETA_S', 'SMB_S', 'HC_S']]
y = data_reg['y']
reg = Regression.linear_regression(x_s, y)
print(reg.params)
print(reg.pvalues)
print(reg.rsquared)
print(reg.rsquared_adj)
rsd = reg.resid
cum_rsd= (1+rsd).cumprod()
dates = list(data_reg.index)

df_cum_yield = pd.DataFrame(index=data.index)
# for col in top_five:
#     r = hv.arithmetic_yield(data[col])
#     df_cum_yield[col] = (1 + r).cumprod()
# df_cum_yield['BETA'] = (1+data['BETA_S']).cumprod()
# df_cum_yield['cum_rsd_801041'] = (1+rsd).cumprod()
df_cum_yield['cum_rsd_index_bysales'] = (1+rsd).cumprod()
df_cum_yield['cum_rsd_beta'] = (1+data['BETA_S']).cumprod()
df_cum_yield['cum_rsd_smb'] = (1+data['SMB_S']).cumprod()
df_cum_yield.to_csv('data/df_cum_yield.csv')
pu.plot_line_chart(dates,[cum_rsd],['cum_rsd'])


def steel_stock_factoring():
    df_res1 = pd.DataFrame(index=data.index)
    df_res2 = pd.DataFrame(index=data.index)
    df_res3 = pd.DataFrame(index=data.index)
    df_params_s = pd.DataFrame()
    df_params_f = pd.DataFrame()
    for id_stock in col_names:
        data_reg = data.copy()
        data_reg['y'] = hv.arithmetic_yield(data_reg[id_stock])

        data_reg_s = data_reg[['y','BETA_S', 'SMB_S', 'HC_S']].dropna()
        x_s = data_reg_s[['BETA_S', 'SMB_S', 'HC_S']]
        y = data_reg_s['y']
        reg_s = Regression.linear_regression(x_s, y)
        rsd_s = reg_s.resid
        df_res1['cum_rsd_s_'+id_stock] = (1 + rsd_s).cumprod()

        data_reg_f = data_reg[['y','BETA_F', 'SMB_F', 'HC_F']].dropna()
        x_f = data_reg_f[['BETA_F', 'SMB_F', 'HC_F']]
        y = data_reg_f['y']
        reg_f = Regression.linear_regression(x_f, y)
        rsd_f = reg_f.resid
        df_res2['cum_rsd_f_'+id_stock] = (1 + rsd_f).cumprod()

        df_res3['cum_' + id_stock] = (1 + data_reg['y']).cumprod()

        params_f = reg_f.params
        params_f['rsquared_f'] = reg_f.rsquared_adj
        params_f['cum_f'] = df_res2['cum_rsd_f_'+id_stock].values[-1]
        params_f['id_stock'] = id_stock
        params_f['t_test'] = flag_t_test(reg_f.pvalues)

        params_s = reg_s.params
        params_s['rsquared_s'] = reg_s.rsquared_adj
        params_s['cum_s'] = df_res1['cum_rsd_s_'+id_stock].values[-1]
        params_s['id_stock'] = id_stock
        params_s['t_test'] = flag_t_test(reg_s.pvalues)

        df_params_s = df_params_s.append(params_s,ignore_index=True)
        df_params_f = df_params_f.append(params_f,ignore_index=True)

    df_res1 = df_res1.dropna(how='all')
    df_res2 = df_res2.dropna(how='all')
    df_res3 = df_res3.dropna(how='all')
    df_res1.to_csv('data/result_reg_stocks1.csv')
    df_res2.to_csv('data/result_reg_stocks2.csv')
    df_res3.to_csv('data/result_reg_stocks3.csv')
    df_params_s.to_csv('data/df_regress_s.csv')
    df_params_f.to_csv('data/df_regress_f.csv')

# steel_stock_factoring()
plt.show()
