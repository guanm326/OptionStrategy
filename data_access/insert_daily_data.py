# encoding: utf-8
import datetime
from WindPy import w
from data_access.db_data_collection import DataCollection
from back_test.model.constant import Util
from Utilities import admin_write_util as admin
import pandas as pd
import numpy as np

w.start()


# date = datetime.date.today()
date = datetime.date(2019,1,25)

dt_date = date.strftime("%Y-%m-%d")
print(dt_date)

conn = admin.conn_mktdata()
conn_intraday = admin.conn_intraday()
conn_gc = admin.conn_gc()

options_mktdata_daily = admin.table_options_mktdata()
futures_mktdata = admin.table_futures_mktdata() # 中金所金融期货仍放在mktdata
futures_mktdata_gc = admin.table_futures_mktdata_gc() # 商品期货放在golden_copy
option_contracts = admin.table_option_contracts()
future_contracts = admin.table_future_contracts() # 只包含中金所金融期货
index_daily = admin.table_indexes_mktdata()
equity_index_intraday = admin.table_index_mktdata_intraday()
option_mktdata_intraday = admin.table_option_mktdata_intraday()

dc = DataCollection()


####################################### INDEXES ##################################################
#### 1. Get Indexes Market Data.

dict_windcode_id = {"000905.SH":"index_500sh",
                    "000300.SH":'index_300sh',
                    "000016.SH":'index_50sh',
                    "510050.SH":'index_50etf'}
for windcode in dict_windcode_id.keys():
    id_instrument = dict_windcode_id[windcode]
    data = w.wsd(windcode, "open,high,low,close,volume,amt",dt_date, dt_date, "")
    df = pd.DataFrame(data=np.transpose(data.Data), columns=data.Fields)
    df.loc[:,Util.DT_DATE] = data.Times
    df.loc[:,Util.ID_INSTRUMENT] = id_instrument
    df.loc[:,'datasource'] = 'wind'
    df.loc[:,Util.CODE_INSTRUMENT] = windcode
    df.loc[:,'timestamp']= datetime.datetime.today()
    df = df.rename(columns={'OPEN':Util.AMT_OPEN,'HIGH':Util.AMT_HIGH,'LOW':Util.AMT_LOW,
                            'CLOSE':Util.AMT_CLOSE,'VOLUME':Util.AMT_TRADING_VOLUME,'AMT':Util.AMT_TRADING_VALUE})
    df = df.dropna()
    try:
        df.to_sql('indexes_mktdata', con=admin.engine_gc, if_exists='append', index=False)
        print('Indexes Market Data : '+id_instrument+' -- inserted into data base succefully')
    except:
        pass

####################################### FUTURES ##################################################
#### 1. Get trading futures contract info(IF/IH/IC).
db_datas = dc.table_future_contracts().wind_cfe_contracts()
for db_data in db_datas:
    id_instrument = db_data['id_instrument']
    res = future_contracts.select(future_contracts.c.id_instrument == id_instrument).execute()
    if res.rowcount > 0: continue
    try:
        conn.execute(future_contracts.insert(), db_data)
        print('future_contracts -- inserted into data base succefully')
    except Exception as e:
        print(e)
        continue

#### 2. Get trading futures market data(IF/IH/IC) :  INTO MKTDATA.FUTURES_MKTDATA
df = dc.table_future_contracts().get_future_contract_ids(dt_date)
for (idx, row) in df.iterrows():
    db_data = dc.table_futures().wind_index_future_daily(dt_date, row['id_instrument'], row['windcode'])
    try:
        conn.execute(futures_mktdata.insert(), db_data)
        print('equity index futures -- inserted into data base succefully')
    except Exception as e:
        print(e)

#TODO: INSERT COMMODITY FUTURE CONTRACTS
#### 3. Get trading futures market data(Commodity Futures).
# product_codes = ['RU.SHF', 'CU.SHF', 'C.DCE', 'M.DCE', 'CF.CZC', 'SR.CZC']
product_codes = ['SR.CZC']

for product_code in product_codes:

    df1 = dc.table_futures().wind_future_daily(dt_date,product_code)
    try:
        df1.to_sql('futures_mktdata', con=admin.engine_gc, if_exists='append', index=False)
        print('futures_mktdata : '+product_code+' -- inserted into data base succefully')
    except Exception as e:
        print(e)
        pass

# ####################################### OPTIONS ##################################################
#### 1. Get trading options contract info (50etf/m/sr)
db_datas = dc.table_option_contracts().wind_options_50etf()
for db_data in db_datas:
    id_instrument = db_data['id_instrument']
    res = option_contracts.select(option_contracts.c.id_instrument == id_instrument).execute()
    if res.rowcount > 0: continue
    try:
        conn.execute(option_contracts.insert(), db_data)
        print('option_contracts -- inserted into data base succefully')
    except Exception as e:
        print(e)
        print(db_data)
        continue

db_datas = dc.table_option_contracts().wind_options_m()
for db_data in db_datas:
    id_instrument = db_data['id_instrument']
    res = option_contracts.select(option_contracts.c.id_instrument == id_instrument).execute()
    if res.rowcount > 0: continue
    try:
        conn.execute(option_contracts.insert(), db_data)
        print('option_contracts -- inserted into data base succefully')

    except Exception as e:
        print(e)
        print(db_data)
        continue

db_datas = dc.table_option_contracts().wind_options_sr()
for db_data in db_datas:
    id_instrument = db_data['id_instrument']
    res = option_contracts.select(option_contracts.c.id_instrument == id_instrument).execute()
    if res.rowcount > 0: continue
    try:
        conn.execute(option_contracts.insert(), db_data)
        print('option_contracts -- inserted into data base succefully')

    except Exception as e:
        print(e)
        print(db_data)
        continue

#### 2. Get option daily matket data (50etf/m/sr/cu)
db_data = dc.table_options().wind_cu_option(dt_date)
if len(db_data) == 0: print('no data')
try:
    conn_gc.execute(options_mktdata_daily.insert(), db_data)
    print('wind CU option -- inserted into data base succefully')
except Exception as e:
    print(e)

db_data = dc.table_options().wind_data_50etf_option(dt_date)
if len(db_data) == 0: print('no data')
try:
    conn_gc.execute(options_mktdata_daily.insert(), db_data)
    print('wind 50ETF option -- inserted into data base succefully')
except Exception as e:
    print(e)

db_data = dc.table_options().wind_data_m_option(dt_date,dt_date)
if len(db_data) == 0: print('no data')
try:
    conn_gc.execute(options_mktdata_daily.insert(), db_data)
    print('wind m option -- inserted into data base succefully')
except Exception as e:
    print(e)

db_data = dc.table_options().wind_data_sr_option(dt_date,dt_date)
if len(db_data) == 0: print('no data')
try:
    conn_gc.execute(options_mktdata_daily.insert(), db_data)
    print('wind sr option -- inserted into data base succefully')
except Exception as e:
    print(e)


# ######################################## INTRADAY DATA ##############################################
# windcode = "510050.SH"
# id_instrument = 'index_50etf'
# db_data = dc.table_index_intraday().wind_data_equity_index(windcode, dt_date, id_instrument)
# try:
#     conn_intraday.execute(equity_index_intraday.insert(), db_data)
#     print('equity_index_intraday-50etf -- inserted into data base succefully')
# except Exception as e:
#     print(e)
#
# windcode = "000016.SH"
# id_instrument = 'index_50sh'
# db_data = dc.table_index_intraday().wind_data_equity_index(windcode, dt_date, id_instrument)
# try:
#     conn_intraday.execute(equity_index_intraday.insert(), db_data)
#     print('equity_index_intraday-50sh -- inserted into data base succefully')
# except Exception as e:
#     print(e)
#
# windcode = "000300.SH"
# id_instrument = 'index_300sh'
# db_data = dc.table_index_intraday().wind_data_equity_index(windcode, dt_date, id_instrument)
# try:
#     conn_intraday.execute(equity_index_intraday.insert(), db_data)
#     print('equity_index_intraday-300sh -- inserted into data base succefully')
# except Exception as e:
#     print(e)
#
# windcode = "000905.SH"
# id_instrument = 'index_500sh'
# db_data = dc.table_index_intraday().wind_data_equity_index(windcode, dt_date, id_instrument)
# try:
#     conn_intraday.execute(equity_index_intraday.insert(), db_data)
#     print('equity_index_intraday-500sh -- inserted into data base succefully')
# except Exception as e:
#     print(e)
#
# # SH50 ETF OPTION
# df = dc.table_options().get_option_contracts(dt_date)
# for (idx_oc, row) in df.iterrows():
#     db_data = dc.table_option_intraday().wind_data_50etf_option_intraday(dt_date, row)
#     try:
#         conn_intraday.execute(option_mktdata_intraday.insert(), db_data)
#
#     except Exception as e:
#         print(e)
# print('option_mktdata_intraday finished')