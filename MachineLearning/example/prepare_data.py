import datetime
import pandas as pd
import numpy as np
from MachineLearning.data import get_mktdata_future_c1_daily
from MachineLearning.util import Util, HistoricalVolatility
from scipy.stats.stats import pearsonr

dt_start = datetime.date(2010, 1, 1)
dt_end = datetime.date(2018, 12, 31)
name_code = Util.STR_IF
df_daily = get_mktdata_future_c1_daily(dt_start, dt_end, name_code)
df_daily['vol'] = HistoricalVolatility.hist_vol(df_daily[Util.AMT_CLOSE], 20)
df_daily.loc[:, 'vwap'] = df_daily.loc[:, Util.AMT_TRADING_VALUE] / df_daily.loc[:, Util.AMT_TRADING_VOLUME] / 300.0

"""
Calculate alpha 2
"""
alpha2_tmp = (2 * df_daily[Util.AMT_CLOSE] - df_daily[Util.AMT_LOW] - df_daily[Util.AMT_HIGH]) / (
        df_daily[Util.AMT_HIGH] - df_daily[Util.AMT_LOW])
df_daily['alpha2'] = alpha2_tmp.diff(periods=1) * -1
"""
Calculate alpha 3
    def alpha_3(data_array,i=0):
        [close, open, high, low, volume, value] = data_array
        res = 0
        for j in i + np.arange(6):
            if close[j+0] == close[j+1]:
                a = 0
            else:
                if close[j+0] > close[j+1]:
                    a = close[j+0] - min(low[j+0],close[j+1])
                else:
                    a = close[j+0] - max(high[j+0],close[j+1])
            res += a
            print(j,a)
        return res
"""
m, n = df_daily.shape
alpha3 = {}
for index, row in df_daily.iterrows():
    if index - 6 < 0:
        alpha3[index] = np.nan
        continue
    a_sum = 0
    for j in range(-6, 0):
        delay = index + j
        close_delay = df_daily.loc[delay][Util.AMT_CLOSE]
        low_cur = df_daily.loc[delay + 1][Util.AMT_LOW]
        high_cur = df_daily.loc[delay + 1][Util.AMT_HIGH]
        close_cur = df_daily.loc[delay + 1][Util.AMT_CLOSE]
        if close_delay == close_cur:
            a = 0
        else:
            if close_cur > close_delay:
                a = close_cur - min(low_cur, close_delay)
            else:
                a = close_cur - max(high_cur, close_delay)
        a_sum += a
    alpha3[index] = a_sum
df_daily['alpha3'] = pd.Series(alpha3)

"""
alpha_量价背离
"""
alpha4 = {}
for index, row in df_daily.iterrows():
    if index - 6 < 0:
        alpha4[index] = np.nan
        continue
    r, _ = pearsonr(df_daily.iloc[index - 6:index]['vwap'], df_daily.iloc[index - 6:index][Util.AMT_TRADING_VOLUME])
    alpha4[index] = -1 * r
df_daily['alpha_量价背离'] = pd.Series(alpha4)

"""
alpha_开盘缺口
"""
tmp = df_daily[Util.AMT_CLOSE].shift()  # 前收盘
df_daily.loc[:, 'alpha_开盘缺口'] = df_daily.loc[:, Util.AMT_OPEN] / tmp

"""
alpha_异常交易量
"""
tmp = df_daily[Util.AMT_TRADING_VOLUME].rolling(window=6).mean().shift()  # 前6天成交量均值
df_daily.loc[:, 'alpha_异常交易量'] = -1 * df_daily.loc[:, Util.AMT_TRADING_VOLUME] / tmp

"""
alpha_量幅背离
"""
alpha5 = {}
for index, row in df_daily.iterrows():
    if index - 6 < 0:
        alpha5[index] = np.nan
        continue
    t = df_daily.iloc[index - 6:index][Util.AMT_HIGH] / df_daily.iloc[index - 6:index][Util.AMT_LOW]
    v = df_daily.iloc[index - 6:index][Util.AMT_TRADING_VOLUME]
    r, _ = pearsonr(t, v)
    alpha4[index] = -1 * r
df_daily['alpha_量幅背离'] = pd.Series(alpha4)

"""
alpha_my0: (turnover)日度的交易量/持仓量
"""
df_daily.loc[:,'alpha_my0'] = df_daily.loc[:,Util.AMT_TRADING_VOLUME]/df_daily.loc[:,Util.AMT_HOLDING_VOLUME]
"""
alpha_my1:日持仓量增减/成交量
"""
d_holding = df_daily[Util.AMT_HOLDING_VOLUME].diff()
df_daily.loc[:,'alpha_my1'] = d_holding/df_daily.loc[:,Util.AMT_TRADING_VOLUME]
df_data = df_daily.dropna().reset_index(drop=True)
print(df_data)
df_data.to_csv('data.csv', index=False)
