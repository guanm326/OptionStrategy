# encoding: utf-8

import datetime

from WindPy import w

from Utilities import admin_write_util as admin
from data_access.db_data_collection import DataCollection

"""
Option data from Wind
"""

w.start()

conn = admin.conn_gc()
conn_intraday = admin.conn_intraday()

options_mktdata_daily = admin.table_options_mktdata()
option_contracts = admin.table_option_contracts()

dc = DataCollection()
today = datetime.date.today()
# beg_date = datetime.date(2015, 1, 1)
beg_date = datetime.date(2018, 12, 1).strftime("%Y-%m-%d")
end_date = datetime.date(2019, 1, 8).strftime("%Y-%m-%d")

date_range = w.tdays(beg_date, end_date, "").Data[0]
date_range = sorted(date_range, reverse=True)
# dt_date = dt.strftime("%Y-%m-%d")

# code_list = [
#     # 'M1707',
#     # 'M1708',
#     # 'M1709',
#     # 'M1711',
#     # 'M1712',
#     # 'M1801',
#     # 'M1803',
#     # 'M1805',
#     # 'M1807',
#     # 'M1808',
#     # 'M1809',
#     # 'M1811',
#     'M1812',
#     'M1901',
#     'M1903',
#     'M1905',
#     'M1907',
#     'M1908',
#     'M1909'
# ]

# Current Trading Contracts
# db_data = dc.table_options().wind_data_m_option(beg_date, end_date)
# if len(db_data) == 0: print('no data')
# try:
#     conn.execute(options_mktdata_daily.insert(), db_data)
#     print('wind m option -- inserted into data base succefully')
# except Exception as e:
#     print(e)


    # db_data = dc.table_options().wind_data_sr_option(beg_date, end_date)
    # if len(db_data) == 0: print('no data')
    # try:
    #     conn.execute(options_mktdata_daily.insert(), db_data)
    #     print('wind sr option -- inserted into data base succefully')
    # except Exception as e:
    #     print(e)

    # for dt in date_range:
    #     dt = dt.strftime("%Y-%m-%d")
    #     db_data = dc.table_options().wind_data_50etf_option(dt)
    #     if len(db_data) == 0: print('no data')
    #     try:
    #         conn.execute(options_mktdata_daily.insert(), db_data)
    #         print(dt,' wind 50ETF option -- inserted into data base succefully')
    #     except Exception as e:
    #         print(e)
for dt in date_range:
    dt = dt.strftime("%Y-%m-%d")
    db_data = dc.table_options().wind_cu_option(dt)
    if len(db_data) == 0: print('no data')
    for row in db_data:
        try:
            conn.execute(options_mktdata_daily.insert(), row)
            print(row['dt_date'],' wind CU option -- inserted into data base succefully')
        except Exception as e:
            print(row['dt_date'],' exception')
