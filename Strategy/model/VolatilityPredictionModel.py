from back_test.model.base_option_set import BaseOptionSet
from back_test.model.base_account import BaseAccount
import data_access.get_data as get_data
import back_test.model.constant as c
import datetime
import numpy as np
from OptionStrategyLib.OptionReplication.synthetic_option import SytheticOption
from Utilities.PlotUtil import PlotUtil
import matplotlib.pyplot as plt
import pandas as pd
from back_test.model.trade import Order
from OptionStrategyLib.VolatilityModel.historical_volatility import HistoricalVolatilityModels as histvol


def iv_hv(date,df_data,cd_iv,cd_hv):
    iv = df_data.loc[date,cd_iv]




name_code = c.Util.STR_IH
name_code_option = c.Util.STR_50ETF
df_metrics = get_data.get_50option_mktdata(start_date, end_date)
df_future_c1_daily = get_data.get_mktdata_future_c1_daily(dt_histvol, end_date, name_code)
df_futures_all_daily = get_data.get_mktdata_future_daily(start_date, end_date,
                                                         name_code)  # daily data of all future contracts

df_future_c1_daily['amt_hv'] = histvol.hist_vol(df_future_c1_daily[c.Util.AMT_CLOSE])
df_iv = get_data.get_iv_by_moneyness(dt_histvol, end_date, c.Util.STR_50ETF)
df_iv_htbr = df_iv[df_iv[c.Util.CD_OPTION_TYPE]=='put_call_htbr']