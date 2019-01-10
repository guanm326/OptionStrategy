import datetime
import matplotlib.pyplot as plt
import back_test.model.constant as c
import data_access.get_data as get_data
from Utilities.PlotUtil import PlotUtil
from Strategy.model.VolTrading_HvIvSignal import VolTrading,VolTradingLLT,VolTradingIvHv,VolTrading_1

dt_start = datetime.date(2016, 1, 1)
dt_end = datetime.date(2017, 12, 31)
dt_histvol = dt_start - datetime.timedelta(days=300)
name_code = c.Util.STR_IH
name_code_option = c.Util.STR_50ETF
df_metrics = get_data.get_50option_mktdata(dt_start, dt_end)
df_future_c1_daily = get_data.get_mktdata_future_c1_daily(dt_histvol, dt_end, name_code)
df_futures_all_daily = get_data.get_mktdata_future_daily(dt_start, dt_end, name_code)
df_iv = get_data.get_iv_by_moneyness(dt_histvol, dt_end, name_code_option)
df_iv = df_iv[df_iv[c.Util.CD_OPTION_TYPE] == 'put_call_htbr'][[c.Util.DT_DATE, c.Util.PCT_IMPLIED_VOL]].reset_index(drop=True)


pu = PlotUtil()
vol_arbitrage = VolTradingIvHv(dt_start, dt_end, df_metrics, df_iv, df_future_c1_daily, df_futures_all_daily)
vol_arbitrage.n_hv = 10
vol_arbitrage.init()
account = vol_arbitrage.back_test()
res = account.analysis()
print(res)
npv1 = list(account.account[c.Util.PORTFOLIO_NPV])

# vol_arbitrage = VolTradingIvHv(dt_start, dt_end, df_metrics, df_iv, df_future_c1_daily, df_futures_all_daily)
# vol_arbitrage.min_premium = 1.0/100
# vol_arbitrage.init()
# account = vol_arbitrage.back_test()
# account.account.to_csv('../iv_hv_account-test.csv')
# account.trade_records.to_csv('../iv_hv_record-test.csv')
# res = account.analysis()
# print(res)
dates = list(account.account.index)
# npv2 = list(account.account[c.Util.PORTFOLIO_NPV])
pu.plot_line_chart(dates, [npv1], ['VolTradingIvHv'])
# pu.plot_line_chart(dates, [npv1,npv2], ['VolTradingIvHv','VolTradingIvHv2'])


plt.show()
