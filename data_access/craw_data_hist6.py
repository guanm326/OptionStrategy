# encoding: utf-8
import datetime
from WindPy import w
from Utilities import admin_write_util as admin
from data_access.db_data_collection import DataCollection

"""
金融期货
股指
"""

w.start()

conn = admin.conn_mktdata()
conn_gc = admin.conn_gc()
futures_mktdata = admin.table_futures_mktdata() # 中金所金融期货仍放在mktdata
future_contracts = admin.table_future_contracts()
dc = DataCollection()



today = datetime.date.today()
beg_date = datetime.date(2010, 1, 1)
end_date = datetime.date(2013,12,31)
# windcode = "000300.SH"
# id_instrument = 'index_300sh'
# windcode = "000016.SH"
# id_instrument = 'index_50sh'
# windcode = "510050.SH"
# id_instrument = 'index_50etf'
# windcode = "000905.SH"
# id_instrument = 'index_500sh'
# data = w.wsd(windcode, "open,high,low,close,volume,amt",beg_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"), "")
#
# df = pd.DataFrame(data=np.transpose(data.Data), columns=data.Fields)
# df.loc[:,Util.DT_DATE] = data.Times
# df.loc[:,Util.ID_INSTRUMENT] = id_instrument
# df.loc[:,'datasource'] = 'wind'
# df.loc[:,Util.CODE_INSTRUMENT] = windcode
# df.loc[:,'timestamp']= datetime.datetime.today()
# df = df.rename(columns={'OPEN':Util.AMT_OPEN,'HIGH':Util.AMT_HIGH,'LOW':Util.AMT_LOW,
#                         'CLOSE':Util.AMT_CLOSE,'VOLUME':Util.AMT_TRADING_VOLUME,'AMT':Util.AMT_TRADING_VALUE})
# df = df.dropna()
# df.to_sql('indexes_mktdata', con=admin.engine_gc, if_exists='append', index=False)

# db_datas = dc.table_future_contracts().wind_future_contracts("IF.CFE", 300, beg_date.strftime("%Y-%m-%d"),end_date.strftime("%Y-%m-%d"))
# for db_data in db_datas:
#     id_instrument = db_data['id_instrument']
#     res = future_contracts.select(future_contracts.c.id_instrument == id_instrument).execute()
#     if res.rowcount > 0: continue
#     try:
#         conn.execute(future_contracts.insert(), db_data)
#         print('future_contracts -- inserted into data base succefully')
#     except Exception as e:
#         print(e)
#         continue


df = dc.table_future_contracts().get_future_contract_ids(beg_date,end_date)
df = df[df['name_code']=='IF']
for (idx, row) in df.iterrows():
    db_data = dc.table_futures().wind_index_future_daily(beg_date,end_date, row['id_instrument'], row['windcode'])
    try:
        conn.execute(futures_mktdata.insert(), db_data)
        print('equity index futures -- inserted into data base succefully')
    except Exception as e:
        print(e)
