import datetime
from MachineLearning.data import get_index_mktdata, get_index_intraday
from MachineLearning.util import Util
from MachineLearning.model.FactorsTrading import Factors
dt_start = datetime.date(2018,1,1)
dt_end = datetime.date(2018,12,31)
name_code = Util.STR_INDEX_50SH
df_daily = get_index_mktdata(dt_start,dt_end,name_code)
# df_minute = get_index_intraday(dt_start,dt_end,name_code)
print(df_daily)
alpha1 = Factors.alpha_1(df_daily)
print(alpha1)
