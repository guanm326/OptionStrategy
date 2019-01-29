from Utilities.PlotUtil import PlotUtil
import data_access.get_data as get_data
import datetime
from back_test.model.constant import Util,HistoricalVolatility
import matplotlib.pyplot as plt


name_code = Util.STR_RU
df = get_data.get_gc_future_c1_daily(datetime.date(2010,1,1),datetime.date.today(),name_code)
df[name_code+'_hv30D'] = HistoricalVolatility.hist_vol(df[Util.AMT_CLOSE],n=30)

df = df[[Util.DT_DATE,name_code+'_hv30D']].dropna()



pu = PlotUtil()
f = pu.plot_yearly_line_chart(df,name_code+'_hv30D','dt_date')
plt.show()
