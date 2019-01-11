import datetime
import pandas as pd
import matplotlib.pyplot as plt
import back_test.model.constant as c
import data_access.get_data as get_data
from Utilities.PlotUtil import PlotUtil
from Strategy.model.VolTrading import VolTrading, VolTradingLLT, VolTradingIvHv, VolTrading_1
pu = PlotUtil()


dt_start = datetime.date(2015, 1, 1)
dt_end = datetime.date(2018, 10, 8)
dt_histvol = dt_start - datetime.timedelta(days=300)
name_code = c.Util.STR_IH
name_code_option = c.Util.STR_50ETF
df_metrics = get_data.get_50option_mktdata(dt_start, dt_end)
df_future_c1_daily = get_data.get_mktdata_future_c1_daily(dt_histvol, dt_end, name_code)
df_futures_all_daily = get_data.get_mktdata_future_daily(dt_start, dt_end, name_code)
df_iv = get_data.get_iv_by_moneyness(dt_histvol, dt_end, name_code_option)
df_iv = df_iv[df_iv[c.Util.CD_OPTION_TYPE] == 'put_call_htbr'][[c.Util.DT_DATE, c.Util.PCT_IMPLIED_VOL]].reset_index(
    drop=True)

vol_arbitrage = VolTradingIvHv(dt_start, dt_end, df_metrics, df_iv, df_future_c1_daily, df_futures_all_daily)
vol_arbitrage.slippage = 1.0/1000.0
vol_arbitrage.init()
account = vol_arbitrage.back_test()
res = account.analysis()
yearly = account.annual_analyis()
print(res)
print(yearly)
yearly.to_csv('../yearly1.csv')
account.account.to_csv('../account1.csv')
dates = list(account.account.index)
npv = list(account.account[c.Util.PORTFOLIO_NPV])
pu.plot_line_chart(dates, [npv], ['npv'])
plt.show()


# npvs = []
# legends = []
# df_sharpes = pd.DataFrame()
# for h in [10, 15, 20, 30, 60]:
#     # for h in [30]:
#     sharpes = {}
#     for cost in [0.0/100.0, 0.5 / 100.0, 1 / 100.0, 1.5 / 100.0, 2.0 / 100.0, 2.5 / 100.0, 3.0 / 100.0]:
#     # for cost in [0.0/100.0]:
#         vol_arbitrage = VolTradingIvHv(dt_start, dt_end, df_metrics, df_iv, df_future_c1_daily, df_futures_all_daily)
#         vol_arbitrage.n_hv = h
#         vol_arbitrage.min_premium = cost
#         vol_arbitrage.init()
#         account = vol_arbitrage.back_test()
#         res = account.analysis()
#         print(res)
#         npvs.append(list(account.account[c.Util.PORTFOLIO_NPV]))
#         legends.append('VolTrading_hv=' + str(h) + '_c=' + str(cost))
#         sharpes.update({cost: res['sharpe']})
#     df_sharpes[h] = pd.Series(sharpes)
# print(df_sharpes)
# df_sharpes.to_csv('../VolTrading_hv_cost-sharpes.csv')
# dates = list(account.account.index)
# pu.plot_line_chart(dates, npvs)
# plt.show()
