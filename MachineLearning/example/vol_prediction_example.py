import datetime
import pandas as pd
import numpy as np
from MachineLearning.data import get_index_mktdata
from MachineLearning.util import Util, HistoricalVolatility

dt_start = datetime.date(2010, 1, 1)
dt_end = datetime.date(2018, 12, 31)
name_code = Util.STR_INDEX_50SH
df_daily = get_index_mktdata(dt_start, dt_end, name_code)
df_daily['vol'] = HistoricalVolatility.hist_vol(df_daily[Util.AMT_CLOSE], 20)

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
print(df_daily)
