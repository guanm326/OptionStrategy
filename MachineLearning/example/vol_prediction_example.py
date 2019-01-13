import datetime
from data_access.get_data import get_index_mktdata, get_index_intraday
from back_test.model.constant import Util
dt_start = datetime.date(2010,1,1)
dt_end = datetime.date(2018,12,31)
name_code = Util.STR_INDEX_50SH
df_daily = get_index_mktdata(dt_start,dt_end,name_code)
# df_minute = get_index_intraday(dt_start,dt_end,name_code)
print(df_daily)