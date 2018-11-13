from OptionStrategyLib.OptionStrategy.protective_put.HedgeIndexByOptions import HedgeIndexByOptions
import back_test.model.constant as c
import datetime
from data_access import get_data

start_date = datetime.date(2015, 1, 1)
end_date = datetime.date(2018, 11, 1)
dt_histvol = start_date - datetime.timedelta(days=500)

df_metrics = get_data.get_50option_mktdata(start_date, end_date)
df_index = get_data.get_index_mktdata(dt_histvol, end_date, c.Util.STR_INDEX_50ETF)

hedging = HedgeIndexByOptions(df_index,df_metrics)
hedging.back_test()

