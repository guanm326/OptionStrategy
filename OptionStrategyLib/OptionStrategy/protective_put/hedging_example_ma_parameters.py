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
cd_short_ma = 'ma_5'
cd_long_ma = 'ma_60'
# cd_std = 'std_10'
df_sharpe = pd.DataFrame()
df_drawdown = pd.DataFrame()

cd_std = 'std_10'

for cd_long_ma in ['ma_20','ma_30','ma_40','ma_50','ma_60','ma_120']:
    sharpe = pd.Series()
    drawdown = pd.Series()

    for cd_short_ma in ['ma_3','ma_5','ma_10','ma_15']:
        hedging = HedgeIndexByOptions(df_index, df_metrics,
                                       cd_direction_timing=cd_direction_timing,
                                       cd_strategy=cd_strategy, cd_volatility=cd_volatility,
                                       cd_short_ma=cd_short_ma, cd_long_ma=cd_long_ma, cd_std=cd_std)
        account = hedging.back_test()
        res = account.analysis()
        sharpe[cd_short_ma] = res['sharpe']
        drawdown[cd_short_ma] = res['max_drawdown']
        # df_res[cd_long_ma] = res
    df_sharpe[cd_long_ma] = sharpe
    df_drawdown[cd_long_ma] = drawdown
df_sharpe.to_csv('../../accounts_data/hedge_sharpes.csv')
df_drawdown.to_csv('../../accounts_data/hedge_drawdowns.csv')
