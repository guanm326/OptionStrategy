import pandas as pd
from back_test.model.constant import HistoricalVolatility as hv
import numpy as np

# 钢铁行业因子多重共线性

data_1 = pd.read_excel('data/steel_mktdata.xlsx')
data_2 = pd.read_excel('data/steel_industry_data.xlsx',sheetname='data')
data = data_1.join(data_2.set_index('date'), on='date', how='left')

# 期货
data_f = data[['date']]
data_s = data[['date']]
data_f.loc[:,'RB_F'] = hv.arithmetic_yield(data['RB.SHF'])
data_f.loc[:,'HC_F'] = hv.arithmetic_yield(data['HC.SHF'])
data_f.loc[:,'I_F'] = hv.arithmetic_yield(data['I.DCE'])
data_f.loc[:,'J_F'] = hv.arithmetic_yield(data['J.DCE'])
data_f.loc[:, 'steel_profit'] = data_f.loc[:, 'RB_F'] - 0.45 * data_f.loc[:, 'J_F'] - 1.6 * data_f.loc[:, 'I_F']
data_f = data_f.dropna().reset_index(drop=True)
dt_start = data_f.iloc[0]['date']
# 现货
data_s.loc[:,'RB_S'] = hv.arithmetic_yield(data['RB'])
data_s.loc[:,'HC_S'] = hv.arithmetic_yield(data['HC'])
data_s.loc[:,'I_S'] = hv.arithmetic_yield(data['I'])
data_s.loc[:,'J_S'] = hv.arithmetic_yield(data['J'])
data_s.loc[:,'LC_S'] = hv.arithmetic_yield(data['LC'])
data_s.loc[:,'GC_S'] = hv.arithmetic_yield(data['GC'])
data_s.loc[:, 'steel_profit'] = data_s.loc[:, 'RB_S'] - 0.45 * data_s.loc[:, 'J_S'] - 1.6 * data_s.loc[:, 'I_S']

data_s = data_s[data_s['date']>=dt_start].reset_index(drop=True)

corr_f = np.corrcoef([data_f['RB_F'],data_f['HC_F'],data_f['I_F'],data_f['J_F'],data_f['steel_profit']])
print(corr_f)

corr_s = np.corrcoef([data_s['RB_S'],data_s['HC_S'],data_s['LC_S'],data_s['GC_S'],data_s['I_S'],data_s['J_S'],data_s['steel_profit']])
print(corr_s)