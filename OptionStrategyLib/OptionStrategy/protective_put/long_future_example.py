from OptionStrategyLib.OptionStrategy.protective_put.HoldFutureContinuous import HoldFutureContinuous
import back_test.model.constant as c
import datetime
import pandas as pd
from data_access import get_data
from Utilities.PlotUtil import PlotUtil
import matplotlib.pyplot as plt

start_date = datetime.date(2015, 1, 1)
end_date = datetime.date(2018, 11, 1)
dt_histvol = start_date - datetime.timedelta(days=500)

df_index = get_data.get_index_mktdata(dt_histvol, end_date, c.Util.STR_INDEX_50SH)
df_c1 = get_data.get_mktdata_future_c1_daily(dt_histvol, end_date, c.Util.STR_IH)
df_all = get_data.get_mktdata_future_daily(dt_histvol, end_date, c.Util.STR_IH)


df_res = pd.DataFrame()

hedging1 = HoldFutureContinuous(df_c1,df_all,df_index)
account1 = hedging1.back_test()
df_account = account1.account.rename(columns={c.Util.DT_DATE: 'date'})
print('original')
res = account1.analysis()

print(res)


pu = PlotUtil()
dates = list(account1.account.index)
npv = list(account1.account[c.Util.PORTFOLIO_NPV])
base_npv = list(account1.account['baseindex_npv'])

pu.plot_line_chart(dates, [npv, base_npv], ['npv', 'base_npv'])
plt.show()

account1.account.to_csv('../../accounts_data/hedge_account_hold_ih_.csv')
account1.trade_records.to_csv('../../accounts_data/hedge_records_hold_ih_.csv')


