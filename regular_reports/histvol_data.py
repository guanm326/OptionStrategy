from OptionStrategyLib.VolatilityModel.historical_volatility import HistoricalVolatilityModels as Histvol
from back_test.model.base_option_set import BaseOptionSet
from data_access import get_data
import back_test.model.constant as c
import Utilities.admin_util as admin
from sqlalchemy import func
import pandas as pd
import datetime
from pandas import ExcelWriter
from Utilities.PlotUtil import PlotUtil
import matplotlib.pyplot as plt


""" 历史波动率 """


def hist_vol(dt_start, df_future_c1_daily):
    m = 100
    df_future_c1_daily.loc[:, 'histvol_10'] = Histvol.hist_vol(df_future_c1_daily[c.Util.AMT_CLOSE], n=10) * m
    df_future_c1_daily.loc[:, 'histvol_20'] = Histvol.hist_vol(df_future_c1_daily[c.Util.AMT_CLOSE], n=20) * m
    df_future_c1_daily.loc[:, 'histvol_30'] = Histvol.hist_vol(df_future_c1_daily[c.Util.AMT_CLOSE], n=30) * m
    df_future_c1_daily.loc[:, 'histvol_60'] = Histvol.hist_vol(df_future_c1_daily[c.Util.AMT_CLOSE], n=60) * m
    df_future_c1_daily.loc[:, 'histvol_90'] = Histvol.hist_vol(df_future_c1_daily[c.Util.AMT_CLOSE], n=90) * m
    df_future_c1_daily.loc[:, 'histvol_120'] = Histvol.hist_vol(df_future_c1_daily[c.Util.AMT_CLOSE], n=120) * m
    return df_future_c1_daily



pu = PlotUtil()
end_date = datetime.date(2018,12,31)
start_date = datetime.date(2010, 1, 1)

writer = ExcelWriter('../data/histvol_data_python.xlsx')
name_codes = [c.Util.STR_CF, c.Util.STR_C, c.Util.STR_RU, c.Util.STR_M,c.Util.STR_CU]
for (idx, name_code) in enumerate(name_codes):
    print(name_code)
    # df_res = pd.DataFrame()
    df_future_c1_daily = get_data.get_gc_future_c1_daily(start_date, end_date, name_code)
    pu.plot_line_chart(list(df_future_c1_daily[c.Util.DT_DATE]),[list(df_future_c1_daily[c.Util.AMT_CLOSE])],['close_'+name_code])
    df_future_c1_daily = hist_vol(start_date, df_future_c1_daily)
    df_future_c1_daily = df_future_c1_daily.sort_values(by=c.Util.DT_DATE, ascending=False)
    df_future_c1_daily.to_excel(writer, 'hv_'+name_code)
    # pu.plot_line_chart(list(df_future_c1_daily[c.Util.DT_DATE]),[list(df_future_c1_daily['histvol_30'])],['histvol_'+name_code])
# plt.show()

writer.save()
