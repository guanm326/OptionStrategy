# encoding: utf-8
import datetime
from WindPy import w
from data_access import spider_api_dce as dce
from data_access import spider_api_sfe as sfe
from data_access import spider_api_czce as czce
from data_access.db_data_collection import DataCollection
from Utilities import admin_write_util as admin

w.start()

# date = datetime.date.today()
date = datetime.date(2019,1,25)
dt_date = date.strftime("%Y-%m-%d")
conn = admin.conn_mktdata()
futures_mktdata_daily = admin.table_futures_mktdata()
dc = DataCollection()

################################## Future Mktdata from Exchange Website ###################################
# dce futures data
ds = dce.spider_mktdata_day(date, date, 0)
for dt in ds.keys():
    data = ds[dt]
    db_data = dc.table_futures().dce_day(dt, data)
    if len(db_data) == 0: continue
    try:
        conn.execute(futures_mktdata_daily.insert(), db_data)
        print('dce futures data 0 -- inserted into data base succefully')
    except Exception as e:
        print(dt)
        print(e)
        continue

ds = dce.spider_mktdata_night(date, date, 0)
for dt in ds.keys():
    data = ds[dt]
    db_data = dc.table_futures().dce_night(dt, data)
    if len(db_data) == 0: continue
    try:
        conn.execute(futures_mktdata_daily.insert(), db_data)
        print('dce futures data 1 -- inserted into data base succefully')
    except Exception as e:
        print(dt)
        print(e)
        continue

ds = sfe.spider_mktdata(date, date)
for dt in ds.keys():
    data = ds[dt]
    db_data = dc.table_futures().sfe_daily(dt, data)
    print(db_data)
    if len(db_data) == 0: continue
    try:
        conn.execute(futures_mktdata_daily.insert(), db_data)
        print('sfe futures data -- inserted into data base succefully')
    except Exception as e:
        print(dt)
        print(e)
        continue


ds = czce.spider_future(date, date)
for dt in ds.keys():
    data = ds[dt]
    db_data = dc.table_futures().czce_daily(dt, data)
    # print(db_data)
    if len(db_data) == 0:
        print('czce futures data -- no data')
        continue
    try:
        conn.execute(futures_mktdata_daily.insert(), db_data)
        print('czce futures data -- inserted into data base succefully')
    except Exception as e:
        print(dt)
        print(e)
        continue

