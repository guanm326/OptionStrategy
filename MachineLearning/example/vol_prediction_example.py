import datetime
import numpy as np
from MachineLearning.data import get_index_mktdata, get_index_intraday
from MachineLearning.util import Util
from MachineLearning.model.FactorsTrading import Factors
dt_start = datetime.date(2018,1,1)
dt_end = datetime.date(2018,12,31)
name_code = Util.STR_INDEX_50SH
df_daily = get_index_mktdata(dt_start,dt_end,name_code).sort_values(by=Util.DT_DATE,ascending=False)
# print(df_daily)
close = np.array(df_daily[Util.AMT_CLOSE])
open = np.array(df_daily[Util.AMT_OPEN])
high = np.array(df_daily[Util.AMT_HIGH])
low = np.array(df_daily[Util.AMT_LOW])
volume = np.array(df_daily[Util.AMT_TRADING_VOLUME])
value = np.array(df_daily[Util.AMT_TRADING_VALUE])
data_array = [close,open,high,low,volume,value]
# print(close)
alpha2 = Factors.alpha_2(data_array)
print(alpha2)
alpha3 = Factors.alpha_3(data_array)
print(alpha3)
