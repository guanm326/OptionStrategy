# encoding: utf-8

import datetime
from WindPy import w
from data_access import spider_api_dce as dce
from data_access import spider_api_sfe as sfe
from data_access import spider_api_czce as czce
from data_access.db_data_collection import DataCollection
from Utilities import admin_write_util as admin
import pandas as pd
import numpy as np

"""
CU ： 沪铜期货
wind data
"""

w.start()

def fun_id_instrument(df):
    WINDCODE = df['WINDCODE']
    product_code = df['product_code']
    if len(WINDCODE) == len(product_code)+4:
        res = (WINDCODE[-len(WINDCODE):-8] + '_' + WINDCODE[-8:-4]).lower()
    else:
        res = (WINDCODE[-len(WINDCODE):-7] + '_1' + WINDCODE[-7:-4]).lower()
    return res

def fun_name_code(df):
    WINDCODE = df['WINDCODE']
    product_code = df['product_code']
    if len(WINDCODE) == len(product_code)+4:
        res = (WINDCODE[-len(WINDCODE):-8]).lower()
    else:
        res = (WINDCODE[-len(WINDCODE):-7]).lower()
    return res

def wind_future_daily(dt,contracts,product_code):
    datestr = dt.strftime("%Y-%m-%d")
    try:
        res = w.wss(contracts,"pre_close,open,high,low,close,volume,amt,oi,pre_settle,settle,windcode",
                    "tradeDate="+datestr+";priceAdj=U;cycle=D")
        d = res.Data
        f = res.Fields
        df = pd.DataFrame(data=np.transpose(d), columns=f,)
        df1 = df.dropna(subset=['CLOSE'])
        df1['product_code'] = product_code
        df1['id_instrument'] = df1.apply(fun_id_instrument,axis=1)
        df1['name_code'] = df1.apply(fun_name_code,axis=1)
        df1['cd_exchange'] = df1['WINDCODE'].apply(lambda x: x[-3:].lower())
        df1.loc[:,'datasource'] = 'wind'
        df1.loc[:,'timestamp'] = datetime.datetime.today()
        df1.loc[:,'dt_date'] = dt
        df1 = df1.drop('product_code', 1)
        df1=df1.rename(columns={'PRE_CLOSE':'amt_last_close',
                            'OPEN':'amt_open',
                            'HIGH':'amt_high',
                           'LOW':'amt_low',
                           'CLOSE':'amt_close',
                           'VOLUME':'amt_trading_volume',
                           'AMT':'amt_trading_value',
                           'OI':'amt_holding_volume',
                           'PRE_SETTLE':'amt_last_settlement',
                           'SETTLE':'amt_settlement',
                           'WINDCODE':'code_instrument'
        })
        return df1
    except Exception as e:
        print(e)
        return pd.DataFrame()

# def wind_future_daily_czc(dt,contracts):
#     datestr = dt.strftime("%Y-%m-%d")
#     try:
#         res = w.wss(contracts,"pre_close,open,high,low,close,volume,amt,oi,pre_settle,settle,windcode",
#                     "tradeDate="+datestr+";priceAdj=U;cycle=D")
#         d = res.Data
#         f = res.Fields
#         df = pd.DataFrame(data=np.transpose(d), columns=f,)
#         df1 = df.dropna(subset=['CLOSE'])
#         df1['id_instrument'] = df1['WINDCODE'].apply(lambda x:(x[-len(x):-7]+'_1'+x[-7:-4]).lower())
#         df1['name_code'] = df1['WINDCODE'].apply(lambda x:x[-len(x):-7].lower())
#         df1['cd_exchange'] = df1['WINDCODE'].apply(lambda x:x[-3:].lower())
#         df1.loc[:,'datasource'] = 'wind'
#         df1.loc[:,'timestamp'] = datetime.datetime.today()
#         df1.loc[:,'dt_date'] = dt
#         df1=df1.rename(columns={'PRE_CLOSE':'amt_last_close',
#                             'OPEN':'amt_open',
#                             'HIGH':'amt_high',
#                            'LOW':'amt_low',
#                            'CLOSE':'amt_close',
#                            'VOLUME':'amt_trading_volume',
#                            'AMT':'amt_trading_value',
#                            'OI':'amt_holding_volume',
#                            'PRE_SETTLE':'amt_last_settlement',
#                            'SETTLE':'amt_settlement',
#                            'WINDCODE':'code_instrument'
#         })
#         return df1
#     except Exception as e:
#         print(e)
#         return pd.DataFrame()

today = datetime.date.today()
beg_date = datetime.date(2005, 1, 1)
end_date = datetime.date(2009, 12, 31)
wind_code = 'CF.CZC'
# data_contracts = w.wset("futurecc","startdate=2010-01-01;enddate="+end_date.strftime("%Y-%m-%d")+";wind_code=CU.SHF;field=wind_code,contract_issue_date,last_trade_date,last_delivery_mouth")
# data_contracts = w.wset("futurecc","startdate=2018-08-01;enddate=2019-01-8;wind_code=CU.SHF")
# data_contracts = w.wset("futurecc","startdate=2010-01-01;enddate=2019-01-08;wind_code=RU.SHF")
# data_contracts = w.wset("futurecc","startdate=2000-01-01;enddate=2015-12-31;wind_code=C.DCE")
# data_contracts = w.wset("futurecc","startdate=2010-01-01;enddate=2019-01-8;wind_code=M.DCE")
data_contracts = w.wset("futurecc","startdate=2005-01-01;enddate=2009-12-31;wind_code="+wind_code)
# data_contracts = w.wset("futurecc","startdate=2000-01-01;enddate=2015-12-31;wind_code=IF.CFE")
# data_contracts = w.wset("futurecc","startdate=2010-01-01;enddate=2019-01-8;wind_code=SR.CZC")
df_contracts = pd.DataFrame(data=np.transpose(data_contracts.Data), columns=data_contracts.Fields)
date_range = w.tdays(beg_date, end_date, "").Data[0]
date_range = sorted(date_range,reverse=True)
for dt in date_range:
    c_str = ""
    contracts = df_contracts[(df_contracts['contract_issue_date'] <=dt)&(df_contracts['last_delivery_month'] >=dt)]['wind_code'].values
    for c in contracts:
        c_str += c +","
    c_str = c_str[0:len(c_str)-2]
    # c_str += '\"'
    df1 = wind_future_daily(dt,c_str,wind_code)
    try:
        df1.to_sql('futures_mktdata', con=admin.engine_gc, if_exists='append', index=False)
        print(dt, ' finished.')
    except Exception as e:
        print(e)
        pass
