import pandas as pd
import datetime
import Utilities.admin_write_util as admin

df_0 = pd.read_excel('D:/01 work/01 dzqh/00_数据/optiondatabase.xlsx', sheet_name='目录')
df_1 = pd.read_excel('D:/01 work/01 dzqh/00_数据/optiondatabase.xlsx', sheet_name='全球关键波动率指数')
df_2 = pd.read_excel('D:/01 work/01 dzqh/00_数据/optiondatabase.xlsx', sheet_name='上证50etf期权')
df_3 = pd.read_excel('D:/01 work/01 dzqh/00_数据/optiondatabase.xlsx', sheet_name='铜期权')
df_4 = pd.read_excel('D:/01 work/01 dzqh/00_数据/optiondatabase.xlsx', sheet_name='豆粕期权')
df_5 = pd.read_excel('D:/01 work/01 dzqh/00_数据/optiondatabase.xlsx', sheet_name='白糖期权')
print('')
table_option_data = admin.table_option_data()


dict_code = {'dt_date': 'dt_date','dt_date.1':'dt_date','dt_date.2':'dt_date'}
for (i, row) in df_0.iterrows():
    dict_code.update({row['name']: row['id']})
print(dict_code)

df_3_1 = df_3.iloc[:,0:15]
df_3_2 = df_3.iloc[:,16:22]
df_3_3 = df_3.iloc[:,23:53]
print(df_3_1.columns.values)
print(df_3_2.columns.values)
print(df_3_3.columns.values)
df_4_1 = df_4.iloc[:,0:29]
df_4_2 = df_4.iloc[:,30:]
# print(df_4_1.columns.values)
# print(df_4_2.columns.values)
df_5_1 = df_5.iloc[:,0:29]
df_5_2 = df_5.iloc[:,30:]
# print(df_5_1.columns.values)
# print(df_5_2.columns.values)
data = [df_1,df_2,df_3_1,df_3_2,df_3_3,df_4_1,df_4_2,df_5_1,df_5_2]
# data = [df_3_2,df_3_3,df_4_1,df_4_2,df_5_1,df_5_2]

list_res = []
df_1 = df_3_1

for df_1 in data:
    df_res = pd.DataFrame()
    columns = df_1.columns.values
    dict_1 = {}
    for c in columns:
        if c in dict_code.keys():
            dict_1.update({c: dict_code[c]})

    df_1 = df_1[list(dict_1.keys())].rename(columns=dict_1)
    column_names = list(dict_1.values())

    for (i, row) in df_1.iterrows():
        for c in column_names:
            if c == 'dt_date': continue
            if pd.isna(row[c]) or row[c] is None: continue
            id = c + '_' + str(row['dt_date'].strftime("%Y%m%d"))
            df_res = df_res.append({'id': id, 'cd_name': c, 'dt_date': row['dt_date'], 'amt_value': row[c],
                           'timestamp': datetime.datetime.now()}, ignore_index=True)
            list_res.append({'id': id, 'cd_name': c, 'dt_date': row['dt_date'], 'amt_value': row[c],
                           'timestamp': datetime.datetime.now()})
        # break 20180101
    # df_res.to_csv('df.csv')
    # break
    df_res = df_res.drop_duplicates('id')
    df_res.to_sql('option_data', con=admin.engine_dzqh, if_exists='append',index=False)





