# encoding: utf-8

import datetime
from WindPy import w
from data_access import spider_api_dce as dce
from data_access import spider_api_sfe as sfe
from data_access import spider_api_czce as czce
from data_access.db_data_collection import DataCollection
from Utilities import admin_write_util as admin

w.start()

date = datetime.date.today()
# date = datetime.date(2018,12,20)

dt_date = date.strftime("%Y-%m-%d")
print(dt_date)

conn = admin.conn_mktdata()
conn_intraday = admin.conn_intraday()
conn_gc = admin.conn_gc()

options_mktdata_daily = admin.table_options_mktdata()
futures_mktdata_daily = admin.table_futures_mktdata()
futures_institution_positions = admin.table_futures_institution_positions()
option_contracts = admin.table_option_contracts()
future_contracts = admin.table_future_contracts()
index_daily = admin.table_indexes_mktdata()

equity_index_intraday = admin.table_index_mktdata_intraday()
option_mktdata_intraday = admin.table_option_mktdata_intraday()

dc = DataCollection()

####################################### Contract base info ##################################################

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

# future_contracts

category_code = "IF.CFE"
nbr_multiplier = 300
db_datas = dc.table_future_contracts().wind_future_contracts(category_code, nbr_multiplier)
for db_data in db_datas:
    id_instrument = db_data['id_instrument']
    res = future_contracts.select(future_contracts.c.id_instrument == id_instrument).execute()
    if res.rowcount > 0: continue
    try:
        conn.execute(future_contracts.insert(), db_data)
        print('future_contracts -- inserted into data base succefully')

    except Exception as e:
        print(e)
        print(db_data)
        continue

category_code = "IH.CFE"
nbr_multiplier = 300
db_datas = dc.table_future_contracts().wind_future_contracts(category_code, nbr_multiplier)
for db_data in db_datas:
    id_instrument = db_data['id_instrument']
    res = future_contracts.select(future_contracts.c.id_instrument == id_instrument).execute()
    if res.rowcount > 0: continue
    try:
        conn.execute(future_contracts.insert(), db_data)
        print('future_contracts -- inserted into data base succefully')

    except Exception as e:
        print(e)
        print(db_data)
        continue

category_code = "IC.CFE"
nbr_multiplier = 200
db_datas = dc.table_future_contracts().wind_future_contracts(category_code, nbr_multiplier)
for db_data in db_datas:
    id_instrument = db_data['id_instrument']
    res = future_contracts.select(future_contracts.c.id_instrument == id_instrument).execute()
    if res.rowcount > 0: continue
    try:
        conn.execute(future_contracts.insert(), db_data)
        print('future_contracts -- inserted into data base succefully')

    except Exception as e:
        print(e)
        print(db_data)
        continue

##################################### MKT DAILY #############################################

# wind CU option

db_data = dc.table_options().wind_cu_option(dt_date)
if len(db_data) == 0: print('no data')
try:
    conn_gc.execute(options_mktdata_daily.insert(), db_data)
    print('wind CU option -- inserted into data base succefully')
except Exception as e:
    print(e)

# wind 50ETF option
res = options_mktdata_daily.select((options_mktdata_daily.c.dt_date == dt_date)
                                   & (options_mktdata_daily.c.name_code == '50etf')).execute()
if res.rowcount == 0:
    db_data = dc.table_options().wind_data_50etf_option(dt_date)
    if len(db_data) == 0: print('no data')
    try:
        conn_gc.execute(options_mktdata_daily.insert(), db_data)
        print('wind 50ETF option -- inserted into data base succefully')
    except Exception as e:
        print(e)
else:
    print('wind 50ETF option -- already exists')

# wind M option
res = options_mktdata_daily.select((options_mktdata_daily.c.dt_date == dt_date)
                                   & (options_mktdata_daily.c.name_code == 'm')).execute()
if res.rowcount == 0:
    db_data = dc.table_options().wind_data_m_option(dt_date,dt_date)
    if len(db_data) == 0: print('no data')
    try:
        conn_gc.execute(options_mktdata_daily.insert(), db_data)
        print('wind m option -- inserted into data base succefully')
    except Exception as e:
        print(e)
else:
    print('wind m option -- already exists')

# wind SR option
res = options_mktdata_daily.select((options_mktdata_daily.c.dt_date == dt_date)
                                   & (options_mktdata_daily.c.name_code == 'sr')).execute()
if res.rowcount == 0:
    db_data = dc.table_options().wind_data_sr_option(dt_date,dt_date)
    if len(db_data) == 0: print('no data')
    try:
        conn_gc.execute(options_mktdata_daily.insert(), db_data)
        print('wind sr option -- inserted into data base succefully')
    except Exception as e:
        print(e)
else:
    print('wind sr option -- already exists')

# dce option data (type = 1)
# dce option data --- day
# res = options_mktdata_daily.select((options_mktdata_daily.c.dt_date == dt_date)
#                                    & (options_mktdata_daily.c.cd_exchange == 'dce')
#                                    & (options_mktdata_daily.c.flag_night == 0)).execute()
# if res.rowcount == 0:
#     ds = dce.spider_mktdata_day(date, date, 1)
#     for dt in ds.keys():
#         data = ds[dt]
#         if len(data) == 0: continue
#         db_data = dc.table_options().dce_day(dt, data)
#         if len(db_data) == 0: continue
#         try:
#             conn.execute(options_mktdata_daily.insert(), db_data)
#             print('dce option data 0 -- inserted into data base succefully')
#         except Exception as e:
#             print(dt)
#             print(e)
#             continue
# else:
#     print('dce option 0 -- already exists')
# dce option data --- night
# res = options_mktdata_daily.select((options_mktdata_daily.c.dt_date == dt_date)
#                                    & (options_mktdata_daily.c.cd_exchange == 'dce')
#                                    & (options_mktdata_daily.c.flag_night == 1)).execute()
# if res.rowcount == 0:
#     ds = dce.spider_mktdata_night(date, date, 1)
#     for dt in ds.keys():
#         data = ds[dt]
#         if len(data) == 0: continue
#         db_data = dc.table_options().dce_night(dt, data)
#         if len(db_data) == 0: continue
#         try:
#             conn.execute(options_mktdata_daily.insert(), db_data)
#             print('dce option data 1 -- inserted into data base succefully')
#         except Exception as e:
#             print(dt)
#             print(e)
#             continue
# else:
#     print('dce option 1 -- already exists')

# czce option data
# res = options_mktdata_daily.select((options_mktdata_daily.c.dt_date == dt_date)
#                                    & (options_mktdata_daily.c.cd_exchange == 'czce')).execute()
# if res.rowcount == 0:
#     ds = czce.spider_option(date, date)
#     for dt in ds.keys():
#         data = ds[dt]
#         if len(data) == 0: continue
#         db_data = dc.table_options().czce_daily(dt, data)
#         if len(db_data) == 0: continue
#         try:
#             conn.execute(options_mktdata_daily.insert(), db_data)
#             print('czce option data -- inserted into data base succefully')
#         except Exception as e:
#             print(dt)
#             print(e)
#             continue
# else:
#     print('czce option -- already exists')





# equity index futures
df = dc.table_future_contracts().get_future_contract_ids(dt_date)
for (idx_oc, row) in df.iterrows():
    # print(row)
    db_data = dc.table_futures().wind_index_future_daily(dt_date, row['id_instrument'], row['windcode'])
    # print(db_data)
    try:
        conn.execute(futures_mktdata_daily.insert(), db_data)
        print(row)
        print('equity index futures -- inserted into data base succefully')
    except Exception as e:
        print(e)

# dce futures data
# dce futures data (type = 0), day
res = futures_mktdata_daily.select((futures_mktdata_daily.c.dt_date == dt_date)
                                   & (futures_mktdata_daily.c.cd_exchange == 'dce')
                                   & (futures_mktdata_daily.c.flag_night == 0)).execute()
if res.rowcount == 0:
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
else:
    print('dce future 0 -- already exists')
# dce futures data (type = 0), night
res = futures_mktdata_daily.select((futures_mktdata_daily.c.dt_date == dt_date)
                                   & (futures_mktdata_daily.c.cd_exchange == 'dce')
                                   & (futures_mktdata_daily.c.flag_night == 1)).execute()
if res.rowcount == 0:
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
else:
    print('dce future 1 -- already exists')

# sfe futures data
res = futures_mktdata_daily.select((futures_mktdata_daily.c.dt_date == dt_date)
                                   & (futures_mktdata_daily.c.cd_exchange == 'sfe')).execute()
# if res.rowcount == 0:
if True:
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
else:
    print('sfe future -- already exists')

# czce futures data
res = futures_mktdata_daily.select((futures_mktdata_daily.c.dt_date == dt_date)
                                   & (futures_mktdata_daily.c.cd_exchange == 'czce')).execute()
if res.rowcount == 0:
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
else:
    print('czce future -- already exists')

## index_mktdata_daily

windcode = "510050.SH"
id_instrument = 'index_50etf'
db_data = dc.table_index().wind_data_index(windcode, dt_date, id_instrument)
try:
    conn.execute(index_daily.insert(), db_data)
    print('equity_index-50etf -- inserted into data base succefully')
except Exception as e:
    print(e)

windcode = "000016.SH"
id_instrument = 'index_50sh'
db_data = dc.table_index().wind_data_index(windcode, dt_date, id_instrument)
try:
    conn.execute(index_daily.insert(), db_data)
    print('equity_index-50sh -- inserted into data base succefully')
except Exception as e:
    print(e)


windcode = "000300.SH"
id_instrument = 'index_300sh'
db_data = dc.table_index().wind_data_index(windcode, dt_date, id_instrument)
try:
    conn.execute(index_daily.insert(), db_data)
    print('equity_index-50etf -- inserted into data base succefully')
except Exception as e:
    print(e)


windcode = "000905.SH"
id_instrument = 'index_500sh'
db_data = dc.table_index().wind_data_index(windcode, dt_date, id_instrument)
try:
    conn.execute(index_daily.insert(), db_data)
    print('equity_index-500sh -- inserted into data base succefully')
except Exception as e:
    print(e)

windcode = "000188.SH"
id_instrument = 'index_cvix'
db_data = dc.table_index().wind_data_index(windcode, dt_date, id_instrument)
try:
    conn.execute(index_daily.insert(), db_data)
    print('equity_index-cvix -- inserted into data base succefully')
except Exception as e:
    print(e)

############################################# MKT INTRADAY #############################################
## index mktdata intraday
# res = equity_index_intraday.select((equity_index_intraday.c.dt_datetime == dt_date + " 09:30:00") &
#                                    (equity_index_intraday.c.id_instrument == 'index_50etf')).execute()
# if res.rowcount == 0:
windcode = "510050.SH"
id_instrument = 'index_50etf'
db_data = dc.table_index_intraday().wind_data_equity_index(windcode, dt_date, id_instrument)
try:
    conn_intraday.execute(equity_index_intraday.insert(), db_data)
    print('equity_index_intraday-50etf -- inserted into data base succefully')
except Exception as e:
    print(e)
# res = equity_index_intraday.select((equity_index_intraday.c.dt_datetime == dt_date + " 09:30:00") &
#                                    (equity_index_intraday.c.id_instrument == 'index_50sh')).execute()
# if res.rowcount == 0:
windcode = "000016.SH"
id_instrument = 'index_50sh'
db_data = dc.table_index_intraday().wind_data_equity_index(windcode, dt_date, id_instrument)
try:
    conn_intraday.execute(equity_index_intraday.insert(), db_data)
    print('equity_index_intraday-50sh -- inserted into data base succefully')
except Exception as e:
    print(e)
# res = equity_index_intraday.select((equity_index_intraday.c.dt_datetime == dt_date + " 09:30:00") &
#                                    (equity_index_intraday.c.id_instrument == 'index_300sh')).execute()
# if res.rowcount == 0:
windcode = "000300.SH"
id_instrument = 'index_300sh'
db_data = dc.table_index_intraday().wind_data_equity_index(windcode, dt_date, id_instrument)
try:
    conn_intraday.execute(equity_index_intraday.insert(), db_data)
    print('equity_index_intraday-300sh -- inserted into data base succefully')
except Exception as e:
    print(e)
# res = equity_index_intraday.select((equity_index_intraday.c.dt_datetime == dt_date + " 09:30:00") &
#                                    (equity_index_intraday.c.id_instrument == 'index_500sh')).execute()
# if res.rowcount == 0:
windcode = "000905.SH"
id_instrument = 'index_500sh'
db_data = dc.table_index_intraday().wind_data_equity_index(windcode, dt_date, id_instrument)
try:
    conn_intraday.execute(equity_index_intraday.insert(), db_data)
    print('equity_index_intraday-500sh -- inserted into data base succefully')
except Exception as e:
    print(e)
# else:
#     print(
#         'equity index intraday -- already exists')

##option_mktdata_intraday
# res = option_mktdata_intraday.select(option_mktdata_intraday.c.dt_datetime == dt_date + " 09:30:00").execute()
# if res.rowcount == 0:
df = dc.table_options().get_option_contracts(dt_date)
for (idx_oc, row) in df.iterrows():
    db_data = dc.table_option_intraday().wind_data_50etf_option_intraday(dt_date, row)
    try:
        conn_intraday.execute(option_mktdata_intraday.insert(), db_data)
        print('option_mktdata_intraday -- inserted into data base succefully')
    except Exception as e:
        print(e)
# else:
#     print('option intraday -- already exists')


########################################### TICK #################################################
# # equity index futures
# res = future_tick_data.select(future_tick_data.c.dt_datetime == dt_date + " 09:30:00").execute()
# if res.rowcount == 0:
#     df = dc.table_future_contracts().get_future_contract_ids(dt_date)
#     for (idx_oc, row) in df.iterrows():
#         db_data = dc.table_future_tick().wind_index_future_tick(dt_date, row['id_instrument'], row['windcode'])
#         try:
#             conn_intraday.execute(future_tick_data.insert(), db_data)
#             # print(row)
#             print(idx_oc,'future_tick_data -- inserted into data base succefully')
#         except Exception as e:
#             print(e)
# else:
#     print('future_tick_data -- already exists')
#
# ##option_tick_data
# res = option_tick_data.select(option_tick_data.c.dt_datetime == dt_date + " 09:30:00").execute()
# if res.rowcount == 0:
#     df = dc.table_options().get_option_contracts(dt_date)
#     for (idx_oc, row) in df.iterrows():
#         db_data = dc.table_option_tick().wind_50etf_option_tick(dt_date, row)
#         try:
#             conn_intraday.execute(option_tick_data.insert(), db_data)
#             print(idx_oc,'option_tick_data -- inserted into data base succefully')
#         except Exception as e:
#             print(e)
# else:
#     print('option_tick_data -- already exists')

#####################CALCULATE OPTION METRICS#########################################
# 50 ETF OPTION
# df_option_metrics = get_50option_mktdata(date,date)
#
# bkt_optionset = BktOptionSet('daily', df_option_metrics, 20)
#
# option_metrics = bkt_optionset.collect_option_metrics()
# try:
#     for r in option_metrics:
#         res = optionMetrics.select((optionMetrics.c.id_instrument == r['id_instrument'])
#                                    & (optionMetrics.c.dt_date == r['dt_date'])).execute()
#         if res.rowcount > 0:
#             optionMetrics.delete((optionMetrics.c.id_instrument == r['id_instrument'])
#                                  & (optionMetrics.c.dt_date == r['dt_date'])).execute()
#         conn_metrics.execute(optionMetrics.insert(), r)
#     print('option metrics -- inserted into data base succefully')
# except Exception as e:
#     print(e)
