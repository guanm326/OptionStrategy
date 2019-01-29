# encoding: utf-8

import datetime
from WindPy import w
from data_access import spider_api_dce as dce
from data_access import spider_api_sfe as sfe
from data_access import spider_api_czce as czce
from data_access.db_data_collection import DataCollection
from Utilities import admin_write_util as admin
from back_test.model.constant import Util
import pandas as pd
import numpy as np

"""
金融期货
股指
"""

w.start()

today = datetime.date.today()
beg_date = datetime.date(2000, 1, 1)
end_date = datetime.date.today()
# windcode = "000300.SH"
# id_instrument = 'index_300sh'
# windcode = "000016.SH"
# id_instrument = 'index_50sh'
# windcode = "510050.SH"
# id_instrument = 'index_50etf'
windcode = "000905.SH"
id_instrument = 'index_500sh'
data = w.wsd(windcode, "open,high,low,close,volume,amt",beg_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"), "")

df = pd.DataFrame(data=np.transpose(data.Data), columns=data.Fields)
df.loc[:,Util.DT_DATE] = data.Times
df.loc[:,Util.ID_INSTRUMENT] = id_instrument
df.loc[:,'datasource'] = 'wind'
df.loc[:,Util.CODE_INSTRUMENT] = windcode
df.loc[:,'timestamp']= datetime.datetime.today()
df = df.rename(columns={'OPEN':Util.AMT_OPEN,'HIGH':Util.AMT_HIGH,'LOW':Util.AMT_LOW,
                        'CLOSE':Util.AMT_CLOSE,'VOLUME':Util.AMT_TRADING_VOLUME,'AMT':Util.AMT_TRADING_VALUE})
df = df.dropna()
df.to_sql('indexes_mktdata', con=admin.engine_gc, if_exists='append', index=False)

