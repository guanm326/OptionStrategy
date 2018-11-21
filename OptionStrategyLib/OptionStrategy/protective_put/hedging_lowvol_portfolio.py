from OptionStrategyLib.OptionStrategy.protective_put.HedgeIndexByOptions import HedgeIndexByOptions
import back_test.model.constant as c
import datetime
import pandas as pd
from data_access import get_data
from Utilities.PlotUtil import PlotUtil
import matplotlib.pyplot as plt
import numpy as np


start_date = datetime.date(2015, 1, 1)
end_date = datetime.date(2018, 11, 1)
dt_histvol = start_date - datetime.timedelta(days=500)


# Base index : TOP50 低波动率组合
data = pd.read_excel('../../../data/TOP50低波组合.xlsx')
data[c.Util.DT_DATE] = data['date'].apply(lambda x: x.date())
data = data[data[c.Util.DT_DATE] >= datetime.date(2015, 1, 1)].reset_index(drop=True)
df_index = data[[c.Util.DT_DATE, 'lowvol']].rename(columns={'lowvol':c.Util.AMT_CLOSE})
df_index[c.Util.ID_INSTRUMENT] = 'top_50_low_vol'
df_index[c.Util.AMT_OPEN] = df_index[c.Util.AMT_CLOSE]
base_index = data[[c.Util.DT_DATE, 'base_index']].rename(columns={'base_index':c.Util.AMT_CLOSE})
df_metrics = get_data.get_50option_mktdata(start_date, end_date)

cd_direction_timing = 'ma'
cd_strategy = 'bull_spread'
cd_volatility = 'close_std'
cd_short_ma = 'ma_3'
cd_long_ma = 'ma_20'
cd_std = 'std_10'

df_res = pd.DataFrame()

hedging1 = HedgeIndexByOptions(df_index, df_metrics,base_index,
                               cd_direction_timing=cd_direction_timing,
                               cd_strategy=cd_strategy, cd_volatility=cd_volatility,
                               cd_short_ma=cd_short_ma, cd_long_ma=cd_long_ma, cd_std=cd_std)

account1 = hedging1.back_test()
df_account = account1.account.rename(columns={c.Util.DT_DATE: 'date'})
print('original')
res = account1.analysis()
res['nbr_timing'] = account1.nbr_timing
print(res)
account1.account.to_csv('../../accounts_data/hedge_account_lowvol_' + cd_short_ma + '_' + cd_long_ma + '_' + cd_std + '.csv')
account1.trade_records.to_csv('../../accounts_data/hedge_records_lowvol_' + cd_short_ma + '_' + cd_long_ma + '_' + cd_std + '.csv')

pu = PlotUtil()
dates = list(account1.account.index)
hedged_npv = list(account1.account[c.Util.PORTFOLIO_NPV])
base_npv = list(account1.account['base_npv'])
pu.plot_line_chart(dates, [hedged_npv, base_npv], ['hedged_npv', 'base_npv'])
plt.show()



# # for P_mdd in [-0.09,-0.08, -0.07, -0.06,-0.05,-0.04]:
# for P_mdd in [-0.07]:
# #     df_account = pd.read_excel('../../accounts_data/hedge_account_'+cd_short_ma+'_'+cd_long_ma+'_'+cd_std+'.xlsx')
# #     df_account['date'] = df_account[c.Util.DT_DATE].apply(lambda x: x.date())
#     hedging = HedgeIndexByOptions(df_index, df_metrics,
#                                   cd_direction_timing=cd_direction_timing,
#                                   cd_strategy=cd_strategy, cd_volatility=cd_volatility,
#                                   cd_short_ma=cd_short_ma, cd_long_ma=cd_long_ma, cd_std=cd_std)
#     drawdown = df_account[['date', c.Util.DRAWDOWN, c.Util.PORTFOLIO_NPV]].set_index('date')
#     account = hedging.back_test_with_stop_loss_1(drawdown, P_mdd)
#     print(P_mdd)
#     res = account.analysis()
#     res['nbr_timing'] = account.nbr_timing
#     res['nbr_stop_loss'] = account.nbr_stop_loss
#     # print(cd_std)
#     print(res)
#     df_res[str(P_mdd)] = res
#     account.account.to_csv('../../accounts_data/hedge_account_sl_'+cd_short_ma+'_'+cd_long_ma+'_'+cd_std+'.csv')
#     account.trade_records.to_csv('../../accounts_data/hedge_records_sl_'+cd_short_ma+'_'+cd_long_ma+'_'+cd_std+'.csv')
#     pu = PlotUtil()
#     dates = list(account.account.index)
#     hedged_npv = list(account.account[c.Util.PORTFOLIO_NPV])
#     base_npv = list(account.account['base_npv'])
#     pu.plot_line_chart(dates, [hedged_npv, base_npv], ['hedged_npv', 'base_npv'])
#     plt.show()
# print(df_res)
# # df_res.to_csv('../../accounts_data/hedge_res_sl_' + cd_short_ma + '_' + cd_long_ma + '.csv')
