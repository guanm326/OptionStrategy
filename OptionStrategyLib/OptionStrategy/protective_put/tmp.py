
from OptionStrategyLib.OptionStrategy.protective_put.HedgeIndexByOptions import HedgeIndexByOptions
import back_test.model.constant as c
import datetime
import pandas as pd
from data_access import get_data
from Utilities.PlotUtil import PlotUtil
import matplotlib.pyplot as plt
import numpy as np
from back_test.model.base_account import BaseAccount

start_date = datetime.date(2015, 1, 1)
end_date = datetime.date(2018, 11, 1)
dt_histvol = start_date - datetime.timedelta(days=500)


# Base index : TOP50 低波动率组合
data = pd.read_excel('../../../data/low_vol.xlsx')
account = BaseAccount(init_fund=c.Util.BILLION, leverage=1.0, rf=0.03)
s = data['npv']
res  = account.get_netvalue_analysis(data['npv'])

# res['turnover'] = account.get_monthly_turnover(data)
print(res)
df_res = pd.DataFrame()
df_res['lowvol'] = res

# Base index
data = pd.read_excel('../../../data/50etf.xlsx')
account = BaseAccount(init_fund=c.Util.BILLION, leverage=1.0, rf=0.03)
s = data['npv']
res  = account.get_netvalue_analysis(data['npv'])

# res['turnover'] = account.get_monthly_turnover(data)
print(res)
df_res['50etf'] = res

data = pd.read_excel('../../../data/50etf_201504.xlsx')
account = BaseAccount(init_fund=c.Util.BILLION, leverage=1.0, rf=0.03)
s = data['npv']
res  = account.get_netvalue_analysis(data['npv'])

# res['turnover'] = account.get_monthly_turnover(data)
print(res)
df_res['50etf_201504'] = res

data = pd.read_excel('../../../data/50etf_hedged_201504.xlsx')
account = BaseAccount(init_fund=c.Util.BILLION, leverage=1.0, rf=0.03)
s = data['npv']
res  = account.get_netvalue_analysis(data['npv'])

# res['turnover'] = account.get_monthly_turnover(data)
print(res)
df_res['50etf_hedged_201504'] = res

data = pd.read_excel('../../../data/base_low_vol.xlsx')
account = BaseAccount(init_fund=c.Util.BILLION, leverage=1.0, rf=0.03)
s = data['npv']
res  = account.get_netvalue_analysis(data['npv'])

# res['turnover'] = account.get_monthly_turnover(data)
print(res)
df_res['base_low_vol'] = res

df_res.to_csv('../../accounts_data/hedge_res.csv')

df_res = pd.DataFrame()
data = pd.read_excel('../../../data/npv2016.xlsx')
account = BaseAccount(init_fund=c.Util.BILLION, leverage=1.0, rf=0.03)
for c in data.columns.values:
    # s = data[c]
    res  = account.get_netvalue_analysis(data[c])
    print(res)
    df_res[c] = res


df_res.to_csv('../../accounts_data/hedge_res_2016.csv')
