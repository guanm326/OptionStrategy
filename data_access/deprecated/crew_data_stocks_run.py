# encoding: utf-8

from sqlalchemy import create_engine, MetaData, Table, Column, TIMESTAMP
import datetime
from WindPy import w
from data_access.db_data_collection import DataCollection

w.start()

# date = datetime.date(2018, 4, 4)
# dt_date = date.strftime("%Y-%m-%d")
# print(dt_date)

engine = create_engine('mysql+pymysql://root:liz1128@101.132.148.152/mktdata', echo=False)
conn = engine.connect()
metadata = MetaData(engine)
stocks = Table('stocks', metadata, autoload=True)
stocks_mktdata = Table('stocks_mktdata', metadata, autoload=True)

dc = DataCollection()


##################### CONTRACT INFO #########################################
# option_contracts

# db_datas = dc.table_stocks().wind_A_shares_total(dt_date)
# for db_data in db_datas:
#     try:
#         conn.execute(stocks.insert(), db_data)
#     except Exception as e:
#         print(e)
#         continue

# for dt in date_range:
#     print(dt)

##################### GET STOCK MKT DATA #########################################
# date = '2018-04-20'
#
# setcode = w.wset("SectorConstituent", u"date=" + date + ";sector=全部A股")
#
# code = setcode.Data[1]
#
# db_datas = dc.table_stocks().wind_stocks_daily_wss(date,code)
# try:
#     conn.execute(stocks_mktdata.insert(), db_datas)
# except Exception as e:
#     print(e)


##################### BATCH GET STOCK MKT DATA #########################################
beg_date = datetime.date(2018, 4, 20)
end_date = datetime.date(2018, 5, 9)

date_range = w.tdays(beg_date, end_date, "").Data[0]
for dt in date_range:
    date = dt.strftime("%Y-%m-%d")
    setcode = w.wset("SectorConstituent", u"date=" + date + ";sector=全部A股")

    code = setcode.Data[1]

    db_datas = dc.table_stocks().wind_stocks_daily_wss(date,code)
    try:
        conn.execute(stocks_mktdata.insert(), db_datas)
    except Exception as e:
        print(e)



##################### RECHECK DATA #########################################

# df_codes = pd.read_excel('../data/recheck.xls',converters={'code_errors': lambda x: str(x)})
# code_errors = df_codes['code_errors'].unique()
#
# df = dc.table_stocks().get_A_shares_total()
#
# df['code'] = df['windcode'].apply(lambda x:x.split('.')[0])
#
# for (i, row) in df.iterrows():
#     if i<4:continue
#     code = row['code']
#     if code in code_errors:
#         windcode = row['windcode']
#         print(windcode)
#         db_datas = dc.table_stocks().wind_stocks_daily(beg_date, end_date, windcode)
#         for db_data in db_datas:
#             # stocks_mktdata.delete((stocks_mktdata.c.id_instrument == db_data['id_instrument'])
#             #                      & (stocks_mktdata.c.dt_date == db_data['dt_date'])
#             #                      & (stocks_mktdata.c.datasource == db_data['datasource'])
#             #                       ).execute()
#             try:
#                 conn.execute(stocks_mktdata.insert(), db_data)
#             except Exception as e:
#                 print(e)
#                 continue
