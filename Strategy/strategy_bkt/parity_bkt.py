import datetime
import pandas as pd
import back_test.model.constant as c
from Strategy.model.PutCallParityArbitrage import ParityArbitrage
from Utilities.PlotUtil import PlotUtil
import matplotlib.pyplot as plt
import data_access.get_data as get_data
start_date = datetime.date(2018, 9, 21)
end_date = datetime.date(2019,1,1)
name_code = c.Util.STR_CU
df_metrics = get_data.get_comoption_mktdata(start_date, end_date,name_code)
df_f_all = get_data.get_gc_future_mktdata(start_date,end_date,name_code)
###################### 50ETF option
# df_sh50=pd.read_excel('../../data/df_sh50.xlsx')
# df_metrics=pd.read_excel('../../data/df_metrics.xlsx')
# df_index= pd.read_excel('../../data/df_index.xlsx')
# df_f_c1=pd.read_excel('../../data/df_f_c1.xlsx')
# df_f_all=pd.read_excel('../../data/df_f_all.xlsx')
#
# df_metrics = df_metrics[(df_metrics[c.Util.DT_DATE]>=start_date)*(df_metrics[c.Util.DT_DATE]<=end_date)].reset_index(drop=True)
# df_index = df_index[(df_index[c.Util.DT_DATE]>=start_date)*(df_index[c.Util.DT_DATE]<=end_date)].reset_index(drop=True)
# df_f_all = df_f_all[(df_f_all[c.Util.DT_DATE]>=start_date)*(df_f_all[c.Util.DT_DATE]<=end_date)].reset_index(drop=True)
# df_sh50 = df_sh50[(df_sh50[c.Util.DT_DATE]>=start_date)*(df_sh50[c.Util.DT_DATE]<=end_date)].reset_index(drop=True)
#
# df_metrics[c.Util.DT_DATE] = df_metrics[c.Util.DT_DATE].apply(lambda x: x.date())
# df_index[c.Util.DT_DATE] = df_index[c.Util.DT_DATE].apply(lambda x: x.date())
# df_f_all[c.Util.DT_DATE] = df_f_all[c.Util.DT_DATE].apply(lambda x: x.date())
# df_sh50[c.Util.DT_DATE] = df_sh50[c.Util.DT_DATE].apply(lambda x: x.date())
#
# df_metrics[c.Util.DT_MATURITY] = df_metrics[c.Util.DT_MATURITY].apply(lambda x: x.date())
# df_f_all[c.Util.DT_MATURITY] = df_f_all[c.Util.DT_MATURITY].apply(lambda x: x.date())
# parity = ParityArbitrage(c.Util.STR_M,df_option=df_metrics,df_etf=df_index,df_future_all=df_f_all,df_index=df_sh50)
# parity.init()
#########################################
parity = ParityArbitrage(name_code,df_option=df_metrics,df_future_all=df_f_all)
parity.init()
account = parity.back_test_comdty('conversion')
parity.df_arbitrage_window.to_csv('../ParityArbitrage-window-cu.csv')
account.account.to_csv('../ParityArbitrage-account-cu.csv')
account.trade_records.to_csv('../ParityArbitrage-records-cu.csv')
print(account.trade_records)
res = account.analysis()
print(res)
pu = PlotUtil()
dates = list(account.account.index)
npv = list(account.account[c.Util.PORTFOLIO_NPV])
pu.plot_line_chart(dates, [npv], ['npv'])
plt.show()

