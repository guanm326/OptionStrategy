from OptionStrategyLib.OptionStrategy.protective_put.HedgeIndexByOptions import HedgeIndexByOptions
import back_test.model.constant as c
import datetime
import pandas as pd
from data_access import get_data
from Utilities.PlotUtil import PlotUtil
import matplotlib.pyplot as plt

start_date = datetime.date(2015, 1, 1)
end_date = datetime.date(2018, 11, 1)
dt_histvol = start_date - datetime.timedelta(days=500)

df_metrics = get_data.get_50option_mktdata(start_date, end_date)
df_index = get_data.get_index_mktdata(dt_histvol, end_date, c.Util.STR_INDEX_50ETF)

cd_direction_timing = 'ma'
cd_strategy = 'bull_spread'
cd_volatility = 'close_std'
cd_short_ma = 'ma_3'
cd_long_ma = 'ma_20'
df_res = pd.DataFrame()

for cd_std in ['std_10','std_5','std_15','std_20']:
# for cd_std in ['std_10']:
    hedging = HedgeIndexByOptions(df_index, df_metrics,
                                  cd_direction_timing=cd_direction_timing,
                                  cd_strategy=cd_strategy, cd_volatility=cd_volatility,
                                  cd_short_ma=cd_short_ma, cd_long_ma=cd_long_ma, cd_std=cd_std)
    account = hedging.back_test()
    res = account.analysis()
    res['nbr_timing'] = account.nbr_timing
    print(res)
    df_res[cd_std] = res

print(df_res)
df_res.to_csv('../../accounts_data/hedge_res_' + cd_short_ma + '_' + cd_long_ma + '.csv')
