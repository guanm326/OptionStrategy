from WindPy import w
import pandas as pd

w.start()
# start_date = "2010-01-01"
start_date = "2010-01-01"
end_date = "2019-01-18"
# 指数价格
data2 = w.wsd("600019.SH,000300.SH,000016.SH,000905.SH,IF.CFE,IH.CFE,IC.CFE,J.DCE,RB.SHF,I.DCE", "close", start_date, end_date, "")
df_mkt = pd.DataFrame(data2.Data, columns=data2.Times, index=data2.Codes).transpose()
df_mkt.loc[:, 'steel_profit'] = df_mkt.loc[:, 'RB.SHF'] - 0.45 * df_mkt.loc[:, 'J.DCE'] - 1.6 * df_mkt.loc[:, 'I.DCE']
# 申万钢铁II：主营业务收入
data = w.wsd(
    "600019.SH,000708.SZ,000709.SZ,000717.SZ,000761.SZ,000778.SZ,000825.SZ,000898.SZ,000932.SZ,000959.SZ,002075.SZ,002110.SZ,002318.SZ,002443.SZ,002478.SZ,002756.SZ,200761.SZ,600010.SH,600022.SH,600117.SH,600126.SH,600231.SH,600282.SH,600307.SH,600399.SH,600507.SH,600569.SH,600581.SH,600782.SH,600808.SH,601003.SH,601005.SH,603878.SH",
    "wgsd_sales_oper", start_date, end_date, "unit=1;rptType=1;currencyType=;Fill=Previous")
# 字段结果相同 : "oper_rev"（营业收入）, oper_rev, tot_oper_rev"
df_sales = pd.DataFrame(data.Data, columns=data.Times, index=data.Codes).transpose()
# 总市值
data0 = w.wsd(
    "600019.SH,000708.SZ,000709.SZ,000717.SZ,000761.SZ,000778.SZ,000825.SZ,000898.SZ,000932.SZ,000959.SZ,002075.SZ,002110.SZ,002318.SZ,002443.SZ,002478.SZ,002756.SZ,200761.SZ,600010.SH,600022.SH,600117.SH,600126.SH,600231.SH,600282.SH,600307.SH,600399.SH,600507.SH,600569.SH,600581.SH,600782.SH,600808.SH,601003.SH,601005.SH,603878.SH",
    "ev", start_date, end_date, "unit=1;rptType=1;currencyType=;Fill=Previous")
df_ev = pd.DataFrame(data0.Data, columns=data0.Times, index=data0.Codes).transpose()
# 收盘价
data1 = w.wsd(
    "600019.SH,000708.SZ,000709.SZ,000717.SZ,000761.SZ,000778.SZ,000825.SZ,000898.SZ,000932.SZ,000959.SZ,002075.SZ,002110.SZ,002318.SZ,002443.SZ,002478.SZ,002756.SZ,200761.SZ,600010.SH,600022.SH,600117.SH,600126.SH,600231.SH,600282.SH,600307.SH,600399.SH,600507.SH,600569.SH,600581.SH,600782.SH,600808.SH,601003.SH,601005.SH,603878.SH",
    "close", start_date, end_date, "")
df_closes = pd.DataFrame(data1.Data, columns=data1.Times, index=data1.Codes).transpose()

# 计算基于主营业务收入的权重
df_sales_weights = df_sales.div(df_sales.sum(axis=1), axis='index')
steel_index = df_closes.mul(df_sales_weights, axis=0).dropna(how='all').sum(axis=1)

df_steel_index = pd.DataFrame()
df_steel_index['steel_index_bysales'] = steel_index
# 计算基于总市值的权重
df_ev_weights = df_ev.div(df_ev.sum(axis=1), axis='index')
steel_index2 = df_closes.mul(df_ev_weights, axis=0).dropna(how='all').sum(axis=1)
df_steel_index['steel_index_byev'] = steel_index2
df = df_steel_index.join(df_mkt, how='left')
df.to_csv('data/steel_mktdata.csv')
df_sales_weights.to_csv('data/df_sales_weights.csv')
