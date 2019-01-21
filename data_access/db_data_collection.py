from sqlalchemy import create_engine, MetaData, Table, Column, TIMESTAMP
from sqlalchemy.orm import sessionmaker
from data_access.db_tables import DataBaseTables as dbt
from WindPy import w
import datetime
import pandas as pd
import numpy as np
from data_access import db_utilities as du
import math
import Utilities.admin_util as admin_read
import Utilities.admin_write_util as admin_write


class DataCollection():
    class table_options():

        def get_option_contracts(self, date, id_underlying='index_50etf'):
            option_contracts = admin_read.table_option_contracts()
            sess = admin_read.session_mktdata()
            query = sess.query(option_contracts.c.dt_listed,
                               option_contracts.c.dt_maturity,
                               option_contracts.c.windcode,
                               option_contracts.c.id_instrument,
                               option_contracts.c.amt_strike,
                               option_contracts.c.cd_option_type
                               ) \
                .filter(option_contracts.c.dt_listed <= date) \
                .filter(option_contracts.c.dt_maturity >= date) \
                .filter(option_contracts.c.id_underlying == id_underlying)
            df_optionchain = pd.read_sql(query.statement, query.session.bind)
            return df_optionchain

        def get_option_contracts_all(self, id_underlying='index_50etf'):
            option_contracts = admin_read.table_option_contracts()
            sess = admin_read.session_mktdata()
            query = sess.query(option_contracts.c.dt_listed,
                               option_contracts.c.dt_maturity,
                               option_contracts.c.windcode,
                               option_contracts.c.id_instrument,
                               option_contracts.c.amt_strike,
                               option_contracts.c.cd_option_type
                               ) \
                .filter(option_contracts.c.id_underlying == id_underlying)
            df_optionchain = pd.read_sql(query.statement, query.session.bind)
            return df_optionchain

        def czce_daily(self, dt, data):
            db_data = []

            cd_exchange = 'czce'
            datasource = 'czce'
            flag_night = -1
            for column in data.columns.values:
                product = data[column]
                product_name = product.loc['品种代码'].lower()
                dt_date = dt
                name_code = product_name[0:2]
                underlying = '1' + product_name[2:5]
                option_type = product_name[5]
                strike = product_name[-4:].replace(',', '').replace(' ', '')
                id_instrument = name_code + '_' + underlying + '_' + option_type + '_' + strike
                id_underlying = name_code + '_' + underlying
                amt_strike = float(strike)
                if option_type == 'c':
                    cd_option_type = 'call'
                else:
                    cd_option_type = 'put'
                amt_last_close = 0.0
                amt_last_settlement = product.loc['昨结算'].replace(',', '')
                amt_open = product.loc['今开盘'].replace(',', '')
                amt_high = product.loc['最高价'].replace(',', '')
                amt_low = product.loc['最低价'].replace(',', '')
                amt_close = product.loc['今收盘'].replace(',', '')
                amt_settlement = product.loc['今结算'].replace(',', '')
                amt_trading_volume = product.loc['成交量(手)'].replace(',', '')
                amt_trading_value = product.loc['成交额(万元)'].replace(',', '')
                amt_holding_volume = product.loc['空盘量'].replace(',', '')
                amt_bid = 0.0
                amt_ask = 0.0
                amt_exercised = product.loc['行权量'].replace(',', '')
                amt_implied_vol = product.loc['隐含波动率'].replace(',', '')
                amt_delta = product.loc['DELTA'].replace(',', '')
                db_row = {'dt_date': dt_date,
                          'id_instrument': id_instrument.encode('utf-8'),
                          'flag_night': flag_night,
                          'datasource': datasource,
                          'name_code': name_code,
                          'id_underlying': id_underlying.encode('utf-8'),
                          'amt_strike': amt_strike,
                          'cd_option_type': cd_option_type.encode('utf-8'),
                          'amt_last_close': amt_last_close,
                          'amt_last_settlement': amt_last_settlement,
                          'amt_open': amt_open,
                          'amt_high': amt_high,
                          'amt_low': amt_low,
                          'amt_close': amt_close,
                          'amt_settlement': amt_settlement,
                          'amt_bid': amt_bid,
                          'amt_ask': amt_ask,
                          'pct_implied_vol': amt_implied_vol,
                          'amt_delta': amt_delta,
                          'amt_trading_volume': amt_trading_volume,
                          'amt_trading_value': amt_trading_value,
                          'amt_holding_volume': amt_holding_volume,
                          'amt_exercised': amt_exercised,
                          'cd_exchange': cd_exchange,
                          'timestamp': datetime.datetime.today()
                          }
                db_data.append(db_row)
            return db_data

        def dce_day(self, dt, data):
            db_data = []
            cd_exchange = 'dce'
            datasource = 'dce'
            flag_night = 0
            for column in data.columns.values:
                product = data[column]
                product_name = product.loc['合约名称'].lower()
                dt_date = dt
                name_code = product_name[0:product_name.index('1')]
                id_underlying = name_code + '_' + product_name[product_name.index('1'):product_name.index('1') + 4]
                option_type = product_name[product_name.index('-') + 1]
                strike = product_name[-4:].replace(',', '').replace(' ', '')
                id_instrument = id_underlying + '_' + option_type + '_' + strike
                amt_strike = float(strike)
                if option_type == 'c':
                    cd_option_type = 'call'
                else:
                    cd_option_type = 'put'
                amt_last_close = 0.0
                amt_last_settlement = product.loc['前结算价'].replace(',', '')
                amt_open = product.loc['开盘价'].replace(',', '')
                amt_high = product.loc['最高价'].replace(',', '')
                amt_low = product.loc['最低价'].replace(',', '')
                amt_close = product.loc['收盘价'].replace(',', '')
                amt_settlement = product.loc['结算价'].replace(',', '')
                amt_trading_volume = product.loc['成交量'].replace(',', '')
                amt_trading_value = product.loc['成交额'].replace(',', '')
                amt_holding_volume = product.loc['持仓量'].replace(',', '')
                amt_bid = 0.0
                amt_ask = 0.0
                amt_exercised = product.loc['行权量'].replace(',', '')
                amt_implied_vol = 0.0
                amt_delta = product.loc['Delta'].replace(',', '')
                db_row = {'dt_date': dt_date,
                          'id_instrument': id_instrument.encode('utf-8'),
                          'flag_night': flag_night,
                          'datasource': datasource,
                          'name_code': name_code,
                          'id_underlying': id_underlying.encode('utf-8'),
                          'amt_strike': amt_strike,
                          'cd_option_type': cd_option_type.encode('utf-8'),
                          'amt_last_close': amt_last_close,
                          'amt_last_settlement': amt_last_settlement,
                          'amt_open': amt_open,
                          'amt_high': amt_high,
                          'amt_low': amt_low,
                          'amt_close': amt_close,
                          'amt_settlement': amt_settlement,
                          'amt_bid': amt_bid,
                          'amt_ask': amt_ask,
                          'pct_implied_vol': amt_implied_vol,
                          'amt_delta': amt_delta,
                          'amt_trading_volume': amt_trading_volume,
                          'amt_trading_value': amt_trading_value,
                          'amt_holding_volume': amt_holding_volume,
                          'amt_exercised': amt_exercised,
                          'cd_exchange': cd_exchange,
                          'timestamp': datetime.datetime.today()
                          }
                db_data.append(db_row)
            return db_data

        def dce_night(self, dt, data):
            db_data = []
            cd_exchange = 'dce'
            datasource = 'dce'
            flag_night = 1
            for column in data.columns.values:
                product = data[column]
                product_name = product.loc['合约名称'].lower()
                dt_date = dt
                name_code = product_name[0:product_name.index('1')]
                id_underlying = name_code + '_' + product_name[product_name.index('1'):product_name.index('1') + 4]
                option_type = product_name[product_name.index('-') + 1]
                strike = product_name[-4:].replace(',', '').replace(' ', '')
                id_instrument = id_underlying + '_' + option_type + '_' + strike
                amt_strike = float(strike)
                if option_type == 'c':
                    cd_option_type = 'call'
                else:
                    cd_option_type = 'put'
                amt_last_close = 0.0
                amt_last_settlement = product.loc['前结算价'].replace(',', '')
                amt_open = product.loc['开盘价'].replace(',', '')
                amt_high = product.loc['最高价'].replace(',', '')
                amt_low = product.loc['最低价'].replace(',', '')
                amt_close = product.loc['最新价'].replace(',', '')
                amt_settlement = 0.0
                amt_trading_volume = product.loc['成交量'].replace(',', '')
                amt_trading_value = product.loc['成交额'].replace(',', '')
                amt_holding_volume = product.loc['持仓量'].replace(',', '')
                amt_bid = 0.0
                amt_ask = 0.0
                amt_exercised = 0.0
                amt_implied_vol = 0.0
                amt_delta = 0.0
                db_row = {'dt_date': dt_date,
                          'id_instrument': id_instrument.encode('utf-8'),
                          'flag_night': flag_night,
                          'datasource': datasource,
                          'name_code': name_code,
                          'id_underlying': id_underlying.encode('utf-8'),
                          'amt_strike': amt_strike,
                          'cd_option_type': cd_option_type.encode('utf-8'),
                          'amt_last_close': amt_last_close,
                          'amt_last_settlement': amt_last_settlement,
                          'amt_open': amt_open,
                          'amt_high': amt_high,
                          'amt_low': amt_low,
                          'amt_close': amt_close,
                          'amt_settlement': amt_settlement,
                          'amt_bid': amt_bid,
                          'amt_ask': amt_ask,
                          'pct_implied_vol': amt_implied_vol,
                          'amt_delta': amt_delta,
                          'amt_trading_volume': amt_trading_volume,
                          'amt_trading_value': amt_trading_value,
                          'amt_holding_volume': amt_holding_volume,
                          'amt_exercised': amt_exercised,
                          'cd_exchange': cd_exchange,
                          'timestamp': datetime.datetime.today()
                          }
                db_data.append(db_row)
            return db_data

        def wind_cu_option(self,datestr):
            data=w.wss(
                "CU1901C46000.SHF,CU1901C47000.SHF,CU1901C48000.SHF,CU1901C49000.SHF,CU1901C50000.SHF,CU1901C51000.SHF,CU1901C52000.SHF,CU1901C53000.SHF,CU1901C54000.SHF,CU1901P46000.SHF,CU1901P47000.SHF,CU1901P48000.SHF,CU1901P49000.SHF,CU1901P50000.SHF,CU1901P51000.SHF,CU1901P52000.SHF,CU1901P53000.SHF,CU1901P54000.SHF,"
                "CU1902C44000.SHF,CU1902C45000.SHF,CU1902C46000.SHF,CU1902C47000.SHF,CU1902C48000.SHF,CU1902C49000.SHF,CU1902C50000.SHF,CU1902C51000.SHF,CU1902C52000.SHF,CU1902C53000.SHF,CU1902C54000.SHF,CU1902P44000.SHF,CU1902P45000.SHF,CU1902P46000.SHF,CU1902P47000.SHF,CU1902P48000.SHF,CU1902P49000.SHF,CU1902P50000.SHF,CU1902P51000.SHF,CU1902P52000.SHF,CU1902P53000.SHF,CU1902P54000.SHF,CU1903C44000.SHF,CU1903C45000.SHF,CU1903C46000.SHF,CU1903C47000.SHF,CU1903C48000.SHF,CU1903C49000.SHF,CU1903C50000.SHF,CU1903C51000.SHF,CU1903C52000.SHF,CU1903C53000.SHF,CU1903C54000.SHF,CU1903P44000.SHF,CU1903P45000.SHF,CU1903P46000.SHF,CU1903P47000.SHF,CU1903P48000.SHF,CU1903P49000.SHF,CU1903P50000.SHF,CU1903P51000.SHF,CU1903P52000.SHF,CU1903P53000.SHF,CU1903P54000.SHF,CU1904C44000.SHF,CU1904C45000.SHF,CU1904C46000.SHF,CU1904C47000.SHF,CU1904C48000.SHF,CU1904C49000.SHF,CU1904C50000.SHF,CU1904C51000.SHF,CU1904C52000.SHF,CU1904C53000.SHF,CU1904C54000.SHF,CU1904P44000.SHF,CU1904P45000.SHF,CU1904P46000.SHF,CU1904P47000.SHF,CU1904P48000.SHF,CU1904P49000.SHF,CU1904P50000.SHF,CU1904P51000.SHF,CU1904P52000.SHF,CU1904P53000.SHF,CU1904P54000.SHF,CU1905C44000.SHF,CU1905C45000.SHF,CU1905C46000.SHF,CU1905C47000.SHF,CU1905C48000.SHF,CU1905C49000.SHF,CU1905C50000.SHF,CU1905C51000.SHF,CU1905C52000.SHF,CU1905C53000.SHF,CU1905C54000.SHF,CU1905P44000.SHF,CU1905P45000.SHF,CU1905P46000.SHF,CU1905P47000.SHF,CU1905P48000.SHF,CU1905P49000.SHF,CU1905P50000.SHF,CU1905P51000.SHF,CU1905P52000.SHF,CU1905P53000.SHF,CU1905P54000.SHF,CU1906C44000.SHF,CU1906C45000.SHF,CU1906C46000.SHF,CU1906C47000.SHF,CU1906C48000.SHF,CU1906C49000.SHF,CU1906C50000.SHF,CU1906C51000.SHF,CU1906C52000.SHF,CU1906C53000.SHF,CU1906C54000.SHF,CU1906P44000.SHF,CU1906P45000.SHF,CU1906P46000.SHF,CU1906P47000.SHF,CU1906P48000.SHF,CU1906P49000.SHF,CU1906P50000.SHF,CU1906P51000.SHF,CU1906P52000.SHF,CU1906P53000.SHF,CU1906P54000.SHF,CU1907C44000.SHF,CU1907C45000.SHF,CU1907C46000.SHF,CU1907C47000.SHF,CU1907C48000.SHF,CU1907C49000.SHF,CU1907C50000.SHF,CU1907C51000.SHF,CU1907C52000.SHF,CU1907C53000.SHF,CU1907C54000.SHF,CU1907P44000.SHF,CU1907P45000.SHF,CU1907P46000.SHF,CU1907P47000.SHF,CU1907P48000.SHF,CU1907P49000.SHF,CU1907P50000.SHF,CU1907P51000.SHF,CU1907P52000.SHF,CU1907P53000.SHF,CU1907P54000.SHF,CU1908C44000.SHF,CU1908C45000.SHF,CU1908C46000.SHF,CU1908C47000.SHF,CU1908C48000.SHF,CU1908C49000.SHF,CU1908C50000.SHF,CU1908C51000.SHF,CU1908C52000.SHF,CU1908C53000.SHF,CU1908C54000.SHF,CU1908P44000.SHF,CU1908P45000.SHF,CU1908P46000.SHF,CU1908P47000.SHF,CU1908P48000.SHF,CU1908P49000.SHF,CU1908P50000.SHF,CU1908P51000.SHF,CU1908P52000.SHF,CU1908P53000.SHF,CU1908P54000.SHF,CU1909C44000.SHF,CU1909C45000.SHF,CU1909C46000.SHF,CU1909C47000.SHF,CU1909C48000.SHF,CU1909C49000.SHF,CU1909C50000.SHF,CU1909C51000.SHF,CU1909C52000.SHF,CU1909C53000.SHF,CU1909C54000.SHF,CU1909P44000.SHF,CU1909P45000.SHF,CU1909P46000.SHF,CU1909P47000.SHF,CU1909P48000.SHF,CU1909P49000.SHF,CU1909P50000.SHF,CU1909P51000.SHF,CU1909P52000.SHF,CU1909P53000.SHF,CU1909P54000.SHF,CU1910C44000.SHF,CU1910C45000.SHF,CU1910C46000.SHF,CU1910C47000.SHF,CU1910C48000.SHF,CU1910C49000.SHF,CU1910C50000.SHF,CU1910C51000.SHF,CU1910C52000.SHF,CU1910C53000.SHF,CU1910C54000.SHF,CU1910C55000.SHF,CU1910C56000.SHF,CU1910P44000.SHF,CU1910P45000.SHF,CU1910P46000.SHF,CU1910P47000.SHF,CU1910P48000.SHF,CU1910P49000.SHF,CU1910P50000.SHF,CU1910P51000.SHF,CU1910P52000.SHF,CU1910P53000.SHF,CU1910P54000.SHF,CU1910P55000.SHF,CU1910P56000.SHF,CU1911C44000.SHF,CU1911C45000.SHF,CU1911C46000.SHF,CU1911C47000.SHF,CU1911C48000.SHF,CU1911C49000.SHF,CU1911C50000.SHF,CU1911C51000.SHF,CU1911C52000.SHF,CU1911C53000.SHF,CU1911C54000.SHF,CU1911C55000.SHF,CU1911P44000.SHF,CU1911P45000.SHF,CU1911P46000.SHF,CU1911P47000.SHF,CU1911P48000.SHF,CU1911P49000.SHF,CU1911P50000.SHF,CU1911P51000.SHF,CU1911P52000.SHF,CU1911P53000.SHF,CU1911P54000.SHF,CU1911P55000.SHF,CU1912C44000.SHF,CU1912C45000.SHF,CU1912C46000.SHF,CU1912C47000.SHF,CU1912C48000.SHF,CU1912C49000.SHF,CU1912C50000.SHF,CU1912C51000.SHF,CU1912C52000.SHF,CU1912C53000.SHF,CU1912C54000.SHF,CU1912C55000.SHF,CU1912P44000.SHF,CU1912P45000.SHF,CU1912P46000.SHF,CU1912P47000.SHF,CU1912P48000.SHF,CU1912P49000.SHF,CU1912P50000.SHF,CU1912P51000.SHF,CU1912P52000.SHF,CU1912P53000.SHF,CU1912P54000.SHF,CU1912P55000.SHF,CU2001C42000.SHF,CU2001C43000.SHF,CU2001C44000.SHF,CU2001C45000.SHF,CU2001C46000.SHF,CU2001C47000.SHF,CU2001C48000.SHF,CU2001C49000.SHF,CU2001C50000.SHF,CU2001C51000.SHF,CU2001C52000.SHF,CU2001P42000.SHF,CU2001P43000.SHF,CU2001P44000.SHF,CU2001P45000.SHF,CU2001P46000.SHF,CU2001P47000.SHF,CU2001P48000.SHF,CU2001P49000.SHF,CU2001P50000.SHF,CU2001P51000.SHF,CU2001P52000.SHF"
                ,"pre_close,open,high,low,close,volume,amt,oi,oi_chg,pre_settle,settle","tradeDate="+datestr+";priceAdj=U;cycle=D")
            # w.wset("optionchain", "date=2018-09-21;us_code=CU.SHF;option_var=全部;call_put=全部")
            df = pd.DataFrame(data=np.transpose(data.Data), columns=data.Fields)
            df['id'] = data.Codes
            db_data = []
            flag_night = -1
            name_code = 'cu'
            datasource = 'wind'
            cd_exchange = 'shf'
            for (i2, row) in df.iterrows():
                dt_date = datetime.datetime.strptime(datestr, "%Y-%m-%d").date()
                windcode = row['id']
                tmp = row['id'].lower()
                id_instrument = tmp[0:2]+'_'+tmp[2:6]+'_'+tmp[6]+'_'+tmp[7:12]
                amt_strike = tmp[7:11]
                if tmp[6] == 'c':
                    cd_option_type = 'call'
                elif tmp[6] == 'p':
                    cd_option_type = 'put'
                else:
                    cd_option_type = None
                id_underlying = tmp[0:2]+'_'+tmp[2:6]
                amt_last_settlement = row['PRE_SETTLE']
                amt_open = row['OPEN']
                amt_high = row['HIGH']
                amt_low = row['LOW']
                amt_close = row['CLOSE']
                amt_settlement = row['SETTLE']
                amt_trading_volume = row['VOLUME']
                amt_trading_value = row['AMT']
                amt_holding_volume = row['OI']
                if pd.isnull(amt_open): amt_open = -999.0
                if pd.isnull(amt_high): amt_high = -999.0
                if pd.isnull(amt_low): amt_low = -999.0
                if pd.isnull(amt_close): continue
                if pd.isnull(amt_settlement): continue
                if pd.isnull(amt_last_settlement): amt_last_settlement = -999.0
                if pd.isnull(amt_trading_volume): continue
                if pd.isnull(amt_trading_value): continue
                if pd.isnull(amt_holding_volume): amt_holding_volume =  -999.0
                db_row = {'dt_date': dt_date,
                          'id_instrument': id_instrument,
                          'flag_night': flag_night,
                          'datasource': datasource,
                          'code_instrument': windcode,
                          'name_code': name_code,
                          'id_underlying': id_underlying,
                          'amt_strike': float(amt_strike),
                          'cd_option_type': cd_option_type,
                          'amt_last_settlement': float(amt_last_settlement),
                          'amt_open': float(amt_open),
                          'amt_high': float(amt_high),
                          'amt_low': float(amt_low),
                          'amt_close': float(amt_close),
                          'amt_settlement': float(amt_settlement),
                          'amt_trading_volume': float(amt_trading_volume),
                          'amt_trading_value': float(amt_trading_value),
                          'amt_holding_volume': float(amt_holding_volume),
                          'cd_exchange': cd_exchange,
                          'timestamp': datetime.datetime.today()
                          }
                db_data.append(db_row)

            return db_data

        def wind_data_50etf_option(self, datestr):

            db_data = []
            id_underlying = 'index_50etf'
            name_code = '50etf'
            datasource = 'wind'
            cd_exchange = 'sse'
            flag_night = -1

            # df_optionchain = self.get_option_contracts(datestr)
            optionchain = w.wset("optioncontractbasicinfo","exchange=sse;windcode=510050.SH;status=all")
            df_optionchain = pd.DataFrame()
            for i0, f0 in enumerate(optionchain.Fields):
                df_optionchain[f0] = optionchain.Data[i0]
            data = w.wset("optiondailyquotationstastics",
                          "startdate=" + datestr + ";enddate=" + datestr + ";exchange=sse;windcode=510050.SH")
            df_mktdatas = pd.DataFrame()
            for i1, f1 in enumerate(data.Fields):
                df_mktdatas[f1] = data.Data[i1]
            df_mktdatas = df_mktdatas.fillna(-999.0)
            for (i2, df_mktdata) in df_mktdatas.iterrows():
                dt_date = datetime.datetime.strptime(datestr, "%Y-%m-%d").date()
                windcode = df_mktdata['option_code']
                code_instrument = windcode + '.SH'
                option_info = df_optionchain[df_optionchain['wind_code'] == windcode]
                call_or_put = option_info['call_or_put'].values[0]
                expire_date = option_info['expire_date'].values[0]
                amt_strike = option_info['exercise_price'].values[0]
                sec_name = option_info['sec_name'].values[0]
                if call_or_put == '认购':
                    cd_option_type = 'call'
                elif call_or_put == '认沽':
                    cd_option_type = 'put'
                else:
                    cd_option_type = 'none'
                    print('error in call_or_put')
                dt_maturity =  pd.to_datetime(str(expire_date))
                name_contract_month = dt_maturity.strftime("%y%m")
                if sec_name[-1] == 'A':
                    id_instrument = '50etf_' + name_contract_month + '_' + cd_option_type[0] + '_' + str(amt_strike)[
                                                                                                     :6] + '_A'
                else:
                    id_instrument = '50etf_' + name_contract_month + '_' + cd_option_type[0] + '_' + str(amt_strike)[:6]
                amt_last_settlement = df_mktdata['pre_settle']
                amt_open = df_mktdata['open']
                amt_high = df_mktdata['highest']
                amt_low = df_mktdata['lowest']
                amt_close = df_mktdata['close']
                amt_settlement = df_mktdata['settlement_price']
                amt_delta = df_mktdata['delta']
                amt_gamma = df_mktdata['gamma']
                amt_vega = df_mktdata['vega']
                amt_theta = df_mktdata['theta']
                amt_rho = df_mktdata['rho']
                amt_trading_volume = df_mktdata['volume']
                amt_trading_value = df_mktdata['amount']
                amt_holding_volume = df_mktdata['position']
                db_row = {'dt_date': dt_date,
                          'id_instrument': id_instrument,
                          'flag_night': flag_night,
                          'datasource': datasource,
                          'code_instrument': code_instrument,
                          'name_code': name_code,
                          'id_underlying': id_underlying,
                          'amt_strike': float(amt_strike),
                          'cd_option_type': cd_option_type,
                          'amt_last_settlement': float(amt_last_settlement),
                          'amt_open': float(amt_open),
                          'amt_high': float(amt_high),
                          'amt_low': float(amt_low),
                          'amt_close': float(amt_close),
                          'amt_settlement': float(amt_settlement),
                          'amt_delta': float(amt_delta),
                          'amt_gamma': float(amt_gamma),
                          'amt_vega': float(amt_vega),
                          'amt_theta': float(amt_theta),
                          'amt_rho': float(amt_rho),
                          'amt_trading_volume': float(amt_trading_volume),
                          'amt_trading_value': float(amt_trading_value),
                          'amt_holding_volume': float(amt_holding_volume),
                          'cd_exchange': cd_exchange,
                          'timestamp': datetime.datetime.today()
                          }
                db_data.append(db_row)
            return db_data

        def wind_data_m_option(self, start_dates_tr,end_date_str,wind_contract='all'):

            db_data = []
            # id_underlying = wind_contract[0].lower() + '_' + wind_contract[1:5]
            name_code = 'm'
            datasource = 'wind'
            cd_exchange = 'dce'
            flag_night = -1

            data = w.wset("optionfuturesdailyquotation",
                   "exchange=DCE;productcode=M;contract="+wind_contract+";startdate="+start_dates_tr+";enddate="+end_date_str)
            print(data.ErrorCode)
            df_mktdatas = pd.DataFrame()
            for i1, f1 in enumerate(data.Fields):
                df_mktdatas[f1] = data.Data[i1]
            df_mktdatas = df_mktdatas.fillna(-999.0)
            for (i2, df_mktdata) in df_mktdatas.iterrows():
                dt_date = df_mktdata['date'].date()
                option_code = df_mktdata['option_code']
                id_instrument = option_code[0].lower()+'_'+option_code[1:5]+'_'+option_code[6].lower() +'_'+option_code[-4:]
                id_underlying = option_code[0].lower()+'_'+option_code[1:5]
                windcode = option_code[0:5]+option_code[6]+option_code[-4:]+'.DCE'
                amt_strike = option_code[-4:]
                if option_code[6].lower()=='c':
                    cd_option_type = 'call'
                elif option_code[6].lower()=='p':
                    cd_option_type = 'put'
                else:
                    cd_option_type = None

                amt_last_settlement = df_mktdata['pre_settle']
                amt_open = df_mktdata['open']
                amt_high = df_mktdata['highest']
                amt_low = df_mktdata['lowest']
                amt_close = df_mktdata['close']
                amt_settlement = df_mktdata['settle']
                amt_delta = df_mktdata['delta']
                # amt_gamma = df_mktdata['gamma']
                # amt_vega = df_mktdata['vega']
                # amt_theta = df_mktdata['theta']
                # amt_rho = df_mktdata['rho']
                amt_trading_volume = df_mktdata['volume']
                amt_trading_value = df_mktdata['amount']
                amt_holding_volume = df_mktdata['position']
                db_row = {'dt_date': dt_date,
                          'id_instrument': id_instrument,
                          'flag_night': flag_night,
                          'datasource': datasource,
                          'code_instrument': windcode,
                          'name_code': name_code,
                          'id_underlying': id_underlying,
                          'amt_strike': float(amt_strike),
                          'cd_option_type': cd_option_type,
                          'amt_last_settlement': float(amt_last_settlement),
                          'amt_open': float(amt_open),
                          'amt_high': float(amt_high),
                          'amt_low': float(amt_low),
                          'amt_close': float(amt_close),
                          'amt_settlement': float(amt_settlement),
                          'amt_delta': float(amt_delta),
                          'amt_gamma': None,
                          'amt_vega': None,
                          'amt_theta': None,
                          'amt_rho': None,
                          'amt_trading_volume': float(amt_trading_volume),
                          'amt_trading_value': float(amt_trading_value),
                          'amt_holding_volume': float(amt_holding_volume),
                          'cd_exchange': cd_exchange,
                          'timestamp': datetime.datetime.today()
                          }
                db_data.append(db_row)
            return db_data

        def wind_data_sr_option(self, start_dates_tr,end_date_str,wind_contract='all'):

            db_data = []
            # id_underlying = wind_contract[0:2].lower() + '_1' + wind_contract[2:5]
            name_code = 'sr'
            datasource = 'wind'
            cd_exchange = 'czce'
            flag_night = -1

            data = w.wset("optionfuturesdailyquotation",
                   "exchange=CZCE;productcode=SR;contract="+wind_contract+";startdate="+start_dates_tr+";enddate="+end_date_str)
            print(data.ErrorCode)
            df_mktdatas = pd.DataFrame()
            for i1, f1 in enumerate(data.Fields):
                df_mktdatas[f1] = data.Data[i1]
            df_mktdatas = df_mktdatas.fillna(-999.0)
            for (i2, df_mktdata) in df_mktdatas.iterrows():
                dt_date = df_mktdata['date'].date()
                option_code = df_mktdata['option_code']
                # TODO
                id_instrument = option_code[0:2].lower()+'_1'+option_code[2:5]+'_'+option_code[5].lower() +'_'+option_code[-4:]
                id_underlying = option_code[0:2].lower()+'_1'+option_code[2:5]
                windcode = option_code+'.CZC'
                amt_strike = option_code[-4:]
                if option_code[5].lower()=='c':
                    cd_option_type = 'call'
                elif option_code[5].lower()=='p':
                    cd_option_type = 'put'
                else:
                    cd_option_type = None

                amt_last_settlement = df_mktdata['pre_settle']
                amt_open = df_mktdata['open']
                amt_high = df_mktdata['highest']
                amt_low = df_mktdata['lowest']
                amt_close = df_mktdata['close']
                amt_settlement = df_mktdata['settle']
                amt_delta = df_mktdata['delta']
                # amt_gamma = df_mktdata['gamma']
                # amt_vega = df_mktdata['vega']
                # amt_theta = df_mktdata['theta']
                # amt_rho = df_mktdata['rho']
                amt_trading_volume = df_mktdata['volume']
                amt_trading_value = df_mktdata['amount']
                amt_holding_volume = df_mktdata['position']
                db_row = {'dt_date': dt_date,
                          'id_instrument': id_instrument,
                          'flag_night': flag_night,
                          'datasource': datasource,
                          'code_instrument': windcode,
                          'name_code': name_code,
                          'id_underlying': id_underlying,
                          'amt_strike': float(amt_strike),
                          'cd_option_type': cd_option_type,
                          'amt_last_settlement': float(amt_last_settlement),
                          'amt_open': float(amt_open),
                          'amt_high': float(amt_high),
                          'amt_low': float(amt_low),
                          'amt_close': float(amt_close),
                          'amt_settlement': float(amt_settlement),
                          'amt_delta': float(amt_delta),
                          'amt_gamma': None,
                          'amt_vega': None,
                          'amt_theta': None,
                          'amt_rho': None,
                          'amt_trading_volume': float(amt_trading_volume),
                          'amt_trading_value': float(amt_trading_value),
                          'amt_holding_volume': float(amt_holding_volume),
                          'cd_exchange': cd_exchange,
                          'timestamp': datetime.datetime.today()
                          }
                db_data.append(db_row)
            return db_data


    class table_futures():

        def dce_night(self, dt, data):
            db_data = []
            datasource = cd_exchange = 'dce'
            for column in data.columns.values:
                product = data[column]
                code_instrument = du.get_codename(product.loc['商品名称']).replace(',', '').replace(' ', '')
                codename = code_instrument.lower()
                id_instrument = codename + '_' + product.loc['交割月份']
                dt_date = dt
                flag_night = 1
                name_code = codename
                amt_last_close = 0.0
                amt_last_settlement = product.loc['前结算价'].replace(',', '')
                amt_open = product.loc['开盘价'].replace(',', '')
                amt_high = product.loc['最高价'].replace(',', '')
                amt_low = product.loc['最低价'].replace(',', '')
                amt_close = product.loc['最新价'].replace(',', '')
                amt_settlement = 0.0
                amt_trading_volume = product.loc['成交量'].replace(',', '')
                amt_trading_value = product.loc['成交额'].replace(',', '')
                amt_holding_volume = product.loc['持仓量'].replace(',', '')
                db_row = {'dt_date': dt_date,
                          'id_instrument': id_instrument,
                          'flag_night': flag_night,
                          'datasource': datasource,
                          'code_instrument': code_instrument,
                          'name_code': name_code,
                          'amt_last_close': amt_last_close,
                          'amt_last_settlement': amt_last_settlement,
                          'amt_open': amt_open,
                          'amt_high': amt_high,
                          'amt_low': amt_low,
                          'amt_close': amt_close,
                          'amt_settlement': amt_settlement,
                          'amt_trading_volume': amt_trading_volume,
                          'amt_trading_value': amt_trading_value,
                          'amt_holding_volume': amt_holding_volume,
                          'cd_exchange': cd_exchange,
                          'timestamp': datetime.datetime.today()
                          }
                db_data.append(db_row)
            return db_data

        def dce_day(self, dt, data):
            db_data = []
            datasource = cd_exchange = 'dce'
            for column in data.columns.values:
                product = data[column]
                code_instrument = du.get_codename(product.loc['商品名称']).replace(',', '').replace(' ', '')
                codename = code_instrument.lower()
                id_instrument = codename + '_' + product.loc['交割月份']
                dt_date = dt
                flag_night = 0
                name_code = codename
                amt_last_close = 0.0
                amt_last_settlement = product.loc['前结算价'].replace(',', '')
                amt_open = product.loc['开盘价'].replace(',', '')
                amt_high = product.loc['最高价'].replace(',', '')
                amt_low = product.loc['最低价'].replace(',', '')
                amt_close = product.loc['收盘价'].replace(',', '')
                amt_settlement = product.loc['结算价'].replace(',', '')
                amt_trading_volume = product.loc['成交量'].replace(',', '')
                amt_trading_value = product.loc['成交额'].replace(',', '')
                amt_holding_volume = product.loc['持仓量'].replace(',', '')
                db_row = {'dt_date': dt_date,
                          'id_instrument': id_instrument,
                          'flag_night': flag_night,
                          'datasource': datasource,
                          'code_instrument': code_instrument,
                          'name_code': name_code,
                          'amt_last_close': amt_last_close,
                          'amt_last_settlement': amt_last_settlement,
                          'amt_open': amt_open,
                          'amt_high': amt_high,
                          'amt_low': amt_low,
                          'amt_close': amt_close,
                          'amt_settlement': amt_settlement,
                          'amt_trading_volume': amt_trading_volume,
                          'amt_trading_value': amt_trading_value,
                          'amt_holding_volume': amt_holding_volume,
                          'cd_exchange': cd_exchange,
                          'timestamp': datetime.datetime.today()
                          }
                db_data.append(db_row)
            return db_data

        def sfe_daily(self, dt, data):
            key_map = du.key_map_sfe()
            data_dict1 = data['o_curinstrument']
            db_data = []
            datasource = cd_exchange = 'sfe'
            for dict in data_dict1:
                name = dict[key_map['codename']].replace(' ', '')
                contractmonth = dict[key_map['contractmonth']].replace(' ', '')
                if name[0:2] == '总计' or contractmonth == '小计': continue
                try:
                    name_code = name[0:name.index('_')].lower()
                except:
                    print(name)
                    continue
                id_instrument = (name_code + '_' + contractmonth).encode('utf-8')
                dt_date = dt
                flag_night = -1
                amt_last_close = dict[key_map['amt_last_close']]
                amt_last_settlement = dict[key_map['amt_last_settlement']]
                amt_open = dict[key_map['amt_open']]
                amt_high = dict[key_map['amt_high']]
                amt_low = dict[key_map['amt_low']]
                amt_close = dict[key_map['amt_close']]
                amt_settlement = dict[key_map['amt_settlement']]
                amt_trading_volume = dict[key_map['amt_trading_volume']]
                amt_trading_value = 0.0
                amt_holding_volume = dict[key_map['amt_holding_volume']]
                if amt_last_close == '': amt_last_close = 0.0
                if amt_last_settlement == '': amt_last_settlement = 0.0
                if amt_open == '': amt_open = 0.0
                if amt_high == '': amt_high = 0.0
                if amt_low == '': amt_low = 0.0
                if amt_close == '': amt_close = 0.0
                if amt_settlement == '': amt_settlement = 0.0
                if amt_trading_volume == '': amt_trading_volume = 0.0
                if amt_trading_value == '': amt_trading_value = 0.0
                if amt_holding_volume == '': amt_holding_volume = 0.0

                db_row = {'dt_date': dt_date,
                          'id_instrument': id_instrument,
                          'flag_night': flag_night,
                          'datasource': datasource,
                          'code_instrument': name,
                          'name_code': name_code,
                          'amt_last_close': amt_last_close,
                          'amt_last_settlement': amt_last_settlement,
                          'amt_open': amt_open,
                          'amt_high': amt_high,
                          'amt_low': amt_low,
                          'amt_close': amt_close,
                          'amt_settlement': amt_settlement,
                          'amt_trading_volume': amt_trading_volume,
                          'amt_trading_value': amt_trading_value,
                          'amt_holding_volume': amt_holding_volume,
                          'cd_exchange': cd_exchange,
                          'timestamp': datetime.datetime.today()
                          }
                db_data.append(db_row)
            return db_data

        def czce_daily(self, dt, data):
            db_data = []
            datasource = cd_exchange = 'czce'
            flag_night = -1
            for column in data.columns.values:
                product = data[column]
                code_instrument = product.loc['品种月份'].replace(',', '').replace(' ', '')
                product_name = product.loc['品种月份'].lower().replace(',', '').replace(' ', '')
                dt_date = dt
                name_code = product_name[:-3]
                underlying = '1' + product_name[-3:]
                id_instrument = name_code + '_' + underlying
                amt_last_close = 0.0
                amt_last_settlement = product.loc['昨结算'].replace(',', '')
                amt_open = product.loc['今开盘'].replace(',', '')
                amt_high = product.loc['最高价'].replace(',', '')
                amt_low = product.loc['最低价'].replace(',', '')
                amt_close = product.loc['今收盘'].replace(',', '')
                amt_settlement = product.loc['今结算'].replace(',', '')
                amt_trading_volume = product.loc['成交量(手)'].replace(',', '')
                amt_trading_value = product.loc['成交额(万元)'].replace(',', '')
                amt_holding_volume = 0.0
                db_row = {'dt_date': dt_date,
                          'id_instrument': id_instrument,
                          'flag_night': flag_night,
                          'datasource': datasource,
                          'code_instrument': code_instrument,
                          'name_code': name_code,
                          'amt_last_close': amt_last_close,
                          'amt_last_settlement': amt_last_settlement,
                          'amt_open': amt_open,
                          'amt_high': amt_high,
                          'amt_low': amt_low,
                          'amt_close': amt_close,
                          'amt_settlement': amt_settlement,
                          'amt_trading_volume': amt_trading_volume,
                          'amt_trading_value': amt_trading_value,
                          'amt_holding_volume': amt_holding_volume,
                          'cd_exchange': cd_exchange,
                          'timestamp': datetime.datetime.today()
                          }
                db_data.append(db_row)
            return db_data

        def wind_index_future_daily(self, datestr, id_instrument, windcode):
            db_data = []
            datasource = 'wind'
            flag_night = -1
            cd_exchange = 'cfe'
            name_code = id_instrument[0:2]
            tickdata = w.wsd(windcode,
                             "pre_close,open,high,low,close,volume,amt,oi,pre_settle,settle",
                             datestr, datestr, "")
            if tickdata.ErrorCode != 0:
                print('wind get data error ', datestr, ',errorcode : ', tickdata.ErrorCode)
                return []
            df = pd.DataFrame()
            for i, f in enumerate(tickdata.Fields):
                df[f] = tickdata.Data[i]
            df['dt_datetime'] = tickdata.Times
            df = df.fillna(0.0)
            for (idx, row) in df.iterrows():
                dt = row['dt_datetime']
                dt_date = datetime.date(dt.year, dt.month, dt.day)
                open_price = row['OPEN']
                high = row['HIGH']
                low = row['LOW']
                close = row['CLOSE']
                volume = row['VOLUME']
                amt = row['AMT']
                amt_holding_volume = row['OI']

                amt_last_close = row['PRE_CLOSE']
                amt_last_settlement = row['PRE_SETTLE']
                amt_settlement = row['SETTLE']
                db_row = {'dt_date': dt_date,
                          'id_instrument': id_instrument,
                          'flag_night': flag_night,
                          'datasource': datasource,
                          'code_instrument': windcode,
                          'name_code': name_code,
                          'amt_last_close': amt_last_close,
                          'amt_last_settlement': amt_last_settlement,
                          'amt_open': open_price,
                          'amt_high': high,
                          'amt_low': low,
                          'amt_close': close,
                          'amt_settlement': amt_settlement,
                          'amt_trading_volume': volume,
                          'amt_trading_value': amt,
                          'amt_holding_volume': amt_holding_volume,
                          'cd_exchange': cd_exchange,
                          'timestamp': datetime.datetime.today()
                          }
                db_data.append(db_row)
            return db_data

        def fun_id_instrument(self,df):
            WINDCODE = df['WINDCODE']
            product_code = df['product_code']
            if len(WINDCODE) == len(product_code) + 4:
                res = (WINDCODE[-len(WINDCODE):-8] + '_' + WINDCODE[-8:-4]).lower()
            else:
                res = (WINDCODE[-len(WINDCODE):-7] + '_1' + WINDCODE[-7:-4]).lower()
            return res

        def fun_name_code(self,df):
            WINDCODE = df['WINDCODE']
            product_code = df['product_code']
            if len(WINDCODE) == len(product_code) + 4:
                res = (WINDCODE[-len(WINDCODE):-8]).lower()
            else:
                res = (WINDCODE[-len(WINDCODE):-7]).lower()
            return res

        def wind_future_daily(self, datestr, contracts, product_code):
            try:
                res = w.wss(contracts, "pre_close,open,high,low,close,volume,amt,oi,pre_settle,settle,windcode",
                            "tradeDate=" + datestr + ";priceAdj=U;cycle=D")
                d = res.Data
                f = res.Fields
                df = pd.DataFrame(data=np.transpose(d), columns=f, )
                df1 = df.dropna(subset=['CLOSE'])
                df1['product_code'] = product_code
                df1['id_instrument'] = df1.apply(self.fun_id_instrument, axis=1)
                df1['name_code'] = df1.apply(self.fun_name_code, axis=1)
                df1['cd_exchange'] = df1['WINDCODE'].apply(lambda x: x[-3:].lower())
                df1.loc[:, 'datasource'] = 'wind'
                df1.loc[:, 'timestamp'] = datetime.datetime.today()
                df1.loc[:, 'dt_date'] = datestr
                df1 = df1.drop('product_code', 1)
                df1 = df1.rename(columns={'PRE_CLOSE': 'amt_last_close',
                                          'OPEN': 'amt_open',
                                          'HIGH': 'amt_high',
                                          'LOW': 'amt_low',
                                          'CLOSE': 'amt_close',
                                          'VOLUME': 'amt_trading_volume',
                                          'AMT': 'amt_trading_value',
                                          'OI': 'amt_holding_volume',
                                          'PRE_SETTLE': 'amt_last_settlement',
                                          'SETTLE': 'amt_settlement',
                                          'WINDCODE': 'code_instrument'
                                          })
                return df1
            except Exception as e:
                print(e)
                return pd.DataFrame()

        # def wind_future_daily(self,datestr, contracts):
        #     try:
        #         res = w.wss(contracts, "pre_close,open,high,low,close,volume,amt,oi,pre_settle,settle,windcode",
        #                     "tradeDate=" + datestr + ";priceAdj=U;cycle=D")
        #         d = res.Data
        #         f = res.Fields
        #         df = pd.DataFrame(data=np.transpose(d), columns=f, )
        #         df1 = df.dropna(subset=['CLOSE'])
        #         df1['id_instrument'] = df1['WINDCODE'].apply(lambda x: (x[-len(x):-8] + '_' + x[-8:-4]).lower())
        #         df1['name_code'] = df1['WINDCODE'].apply(lambda x: x[-len(x):-8].lower())
        #         df1['cd_exchange'] = df1['WINDCODE'].apply(lambda x: x[-3:].lower())
        #         df1.loc[:, 'datasource'] = 'wind'
        #         df1.loc[:, 'timestamp'] = datetime.datetime.today()
        #         df1.loc[:, 'dt_date'] = datestr
        #         df1 = df1.rename(columns={'PRE_CLOSE': 'amt_last_close',
        #                                   'OPEN': 'amt_open',
        #                                   'HIGH': 'amt_high',
        #                                   'LOW': 'amt_low',
        #                                   'CLOSE': 'amt_close',
        #                                   'VOLUME': 'amt_trading_volume',
        #                                   'AMT': 'amt_trading_value',
        #                                   'OI': 'amt_holding_volume',
        #                                   'PRE_SETTLE': 'amt_last_settlement',
        #                                   'SETTLE': 'amt_settlement',
        #                                   'WINDCODE': 'code_instrument'
        #                                   })
        #         return df1
        #     except Exception as e:
        #         print(e)
        #         return pd.DataFrame()
        #
        # # def wind_future_daily_czc(self,datestr, contracts):
        # #     # datestr = dt.strftime("%Y-%m-%d")
        # #     try:
        # #         res = w.wss(contracts, "pre_close,open,high,low,close,volume,amt,oi,pre_settle,settle,windcode",
        # #                     "tradeDate=" + datestr + ";priceAdj=U;cycle=D")
        # #         d = res.Data
        # #         f = res.Fields
        # #         df = pd.DataFrame(data=np.transpose(d), columns=f, )
        # #         df1 = df.dropna(subset=['CLOSE'])
        # #         df1['id_instrument'] = df1['WINDCODE'].apply(lambda x: (x[-len(x):-7] + '_1' + x[-7:-4]).lower())
        # #         df1['name_code'] = df1['WINDCODE'].apply(lambda x: x[-len(x):-7].lower())
        # #         df1['cd_exchange'] = df1['WINDCODE'].apply(lambda x: x[-3:].lower())
        # #         df1.loc[:, 'datasource'] = 'wind'
        # #         df1.loc[:, 'timestamp'] = datetime.datetime.today()
        # #         df1.loc[:, 'dt_date'] = datestr
        # #         df1 = df1.rename(columns={'PRE_CLOSE': 'amt_last_close',
        # #                                   'OPEN': 'amt_open',
        # #                                   'HIGH': 'amt_high',
        # #                                   'LOW': 'amt_low',
        # #                                   'CLOSE': 'amt_close',
        # #                                   'VOLUME': 'amt_trading_volume',
        # #                                   'AMT': 'amt_trading_value',
        # #                                   'OI': 'amt_holding_volume',
        # #                                   'PRE_SETTLE': 'amt_last_settlement',
        # #                                   'SETTLE': 'amt_settlement',
        # #                                   'WINDCODE': 'code_instrument'
        # #                                   })
        # #         return df1
        # #     except Exception as e:
        # #         print(e)
        # #         return pd.DataFrame()

    class table_stocks():

        def wind_A_shares_total(self,datestr):
            db_data = []
            data = w.wset("sectorconstituent","date="+datestr+";sectorid=a001010100000000")
            if data.ErrorCode != 0:
                print('wind get data error ', datestr, ',errorcode : ', data.ErrorCode)
                return []
            df = pd.DataFrame()
            for i, f in enumerate(data.Fields):
                df[f] = data.Data[i]
            for (idx, row) in df.iterrows():
                windcode = row['wind_code']
                name_instrument = row['sec_name'].encode('utf-8')
                db_row = {'id_section': 'A_shares_total',
                          'windcode': windcode,
                          'name_instrument':name_instrument,
                          'timestamp': datetime.datetime.today()
                          }
                db_data.append(db_row)
            return db_data

        def get_A_shares_total(self):
            engine = create_engine('mysql+pymysql://root:liz1128@101.132.148.152/mktdata',
                                   echo=False)
            metadata = MetaData(engine)
            stocks = Table('stocks', metadata, autoload=True)
            Session = sessionmaker(bind=engine)
            sess = Session()
            query = sess.query(stocks.c.id_section,
                               stocks.c.windcode,
                               ) \
                .filter(stocks.c.id_section == 'A_shares_total')
            df = pd.read_sql(query.statement, query.session.bind)
            return df

        def wind_stocks_daily(self,begdate ,enddate, windcode):
            db_data = []
            datasource = 'wind'
            # tickdata = w.wsd(windcode, "pre_close,open,high,low,close,volume,amt,trade_status,sec_name,windcode,exch_eng",
            #                  begdate, enddate, "")
            tickdata = w.wsd(windcode, "pre_close,close,sec_name,windcode,exch_eng",
                             begdate, enddate, "")
            if tickdata.ErrorCode != 0:
                print('wind get data error ', begdate, enddate, ',errorcode : ', tickdata.ErrorCode)
                return []
            df = pd.DataFrame()
            for i, f in enumerate(tickdata.Fields):
                df[f] = tickdata.Data[i]
            df['dt_date'] = tickdata.Times
            df = df.fillna(-1)
            for (idx, row) in df.iterrows():
                dt = row['dt_date']
                dt_date = datetime.date(dt.year, dt.month, dt.day)
                # open_price = row['OPEN']
                # high = row['HIGH']
                # low = row['LOW']
                close = row['CLOSE']
                # volume = row['VOLUME']
                # amt = row['AMT']
                amt_last_close = row['PRE_CLOSE']
                # if open_price ==None : open_price = -1
                # if high==None : high = -1
                # if low==None : low = -1
                # if close==None : close = -1
                # if volume==None : volume = -1
                # if amt==None : amt = -1
                # if amt_last_close==None : amt_last_close = -1
                cd_exchange = row['EXCH_ENG'].lower()
                try :
                    name_instrument = row['SEC_NAME'].encode('utf-8')
                except:
                    name_instrument = 'nan'
                id_instrument = windcode[0:6]+'_'+windcode[-2:]
                db_row = {'dt_date': dt_date,
                          'id_instrument': id_instrument,
                          'datasource': datasource,
                          'code_instrument': windcode,
                          'name_instrument':name_instrument,
                          # 'flag_in_trade':flag_in_trade,
                          'amt_last_close': float(amt_last_close),
                          # 'amt_open': float(open_price),
                          # 'amt_high': float(high),
                          # 'amt_low': float(low),
                          'amt_close': float(close),
                          # 'amt_trading_volume': float(volume),
                          # 'amt_trading_value': float(amt),
                          'cd_exchange': cd_exchange,
                          'timestamp': datetime.datetime.today()
                          }
                db_data.append(db_row)
            return db_data

        def wind_stocks_daily_wss(self,date,codeset):
            db_data = []
            datasource = 'wind'

            setcode = w.wset("SectorConstituent", u"date=" + date + ";sector=全部A股")
            code = setcode.Data[1]
            tickdata = w.wss(code, "close", "tradeDate=" + date + ";priceAdj=U;cycle=D")
            if tickdata.ErrorCode != 0:
                print('wind get data error ', date, ',errorcode : ', tickdata.ErrorCode)
                return []
            df = pd.DataFrame()
            # for i, f in enumerate(tickdata.Fields):
            #     df[f] = tickdata.Data[i]
            codes = tickdata.Codes
            closes = tickdata.Data[0]
            # df = df.fillna(-1)
            # dt = tickdata.Times[0]
            for (idx, windcode) in enumerate(codes):
                dt_date = date
                # close = closes[idx]
                try:
                    close = float(closes[idx])
                except:
                    close = -1
                id_instrument = windcode[0:6]+'_'+windcode[-2:]
                db_row = {'dt_date': dt_date,
                          'id_instrument': id_instrument,
                          'datasource': datasource,
                          'code_instrument': windcode,
                          'amt_close': float(close),
                          'timestamp': datetime.datetime.today()
                          }
                db_data.append(db_row)
            return db_data


    class table_future_contracts():

        def get_future_contract_ids(self, datestr):
            engine = create_engine('mysql+pymysql://root:liz1128@101.132.148.152/mktdata',
                                   echo=False)
            FutureContracts = dbt.Futures
            Session = sessionmaker(bind=engine)
            sess = Session()
            query = sess.query(FutureContracts.id_instrument, FutureContracts.windcode) \
                .filter(datestr >= FutureContracts.dt_listed) \
                .filter(datestr <= FutureContracts.dt_maturity)
            df_windcode = pd.read_sql(query.statement, query.session.bind)
            return df_windcode

        def wind_cfe_contracts(self):
            dict_code_multiplier = {"IF.CFE": 300,
                                    "IH.CFE":300,
                                    "IC.CFE":200}
            db_data = []
            for category_code in dict_code_multiplier.keys():
                nbr_multiplier = dict_code_multiplier[category_code]
                db_data.extend( self.wind_future_contracts(category_code,nbr_multiplier))
            return db_data

        def wind_future_contracts(self, category_code, nbr_multiplier):
            db_data = []

            cd_exchange = 'cfe'
            data = w.wset("futurecc", "wind_code=" + category_code)
            df_contracts = pd.DataFrame()
            for i1, f1 in enumerate(data.Fields):
                df_contracts[f1] = data.Data[i1]
            df_contracts = df_contracts.fillna(-999.0)
            for (idx, df) in df_contracts.iterrows():
                windcode = df['wind_code']
                name_instrument = df['sec_name'].encode('utf-8')
                name_code = df['code'][0:2]
                name_contract_month = df['code'][2:]
                pct_margin = df['target_margin']
                pct_change_limit = df['change_limit']
                dt_listed = df['contract_issue_date'].date()
                dt_maturity = df['last_trade_date'].date()
                # dt_settlement = df['last_delivery_mouth'].date()
                id_instrument = name_code + '_' + name_contract_month

                db_row = {'id_instrument': id_instrument,
                          'windcode': windcode,
                          'name_instrument': name_instrument,
                          'name_code': name_code,
                          'name_contract_month': name_contract_month,
                          'pct_margin': pct_margin,
                          'pct_change_limit': pct_change_limit,
                          'dt_listed': dt_listed,
                          'dt_maturity': dt_maturity,
                          # 'dt_settlement': dt_settlement,
                          'nbr_multiplier': nbr_multiplier,
                          'cd_exchange': cd_exchange,
                          'timestamp': datetime.datetime.today()
                          }
                db_data.append(db_row)
            return db_data

    class table_option_contracts():

        def wind_options_50etf(self):
            db_data = []
            id_underlying = 'index_50etf'
            windcode_underlying = '510050.SH'

            cd_exchange = 'sse'
            data = w.wset("optioncontractbasicinfo", "exchange=sse;windcode=510050.SH;status=trading")
            optionData = data.Data
            optionFlds = data.Fields
            print('ErrorCode : ',data.ErrorCode)
            wind_code = optionData[optionFlds.index('wind_code')]
            trade_code = optionData[optionFlds.index('trade_code')]
            sec_name = optionData[optionFlds.index('sec_name')]
            option_mark_code = optionData[optionFlds.index('option_mark_code')]
            call_or_put = optionData[optionFlds.index('call_or_put')]
            exercise_mode = optionData[optionFlds.index('exercise_mode')]
            exercise_price = optionData[optionFlds.index('exercise_price')]
            contract_unit = optionData[optionFlds.index('contract_unit')]
            limit_month = optionData[optionFlds.index('limit_month')]
            listed_date = optionData[optionFlds.index('listed_date')]
            expire_date = optionData[optionFlds.index('expire_date')]
            exercise_date = optionData[optionFlds.index('exercise_date')]
            settlement_date = optionData[optionFlds.index('settlement_date')]
            settle_mode = optionData[optionFlds.index('settle_mode')]

            for idx, windcode in enumerate(wind_code):
                windcode = windcode + '.SH'
                name_option = sec_name[idx].encode('utf-8')
                if call_or_put[idx] == '认购':
                    cd_option_type = 'call'
                elif call_or_put[idx] == '认沽':
                    cd_option_type = 'put'
                else:
                    cd_option_type = 'none'
                    print('error in call_or_put')
                cd_exercise_type = exercise_mode[idx].encode('utf-8')
                dt_maturity = expire_date[idx].date()
                name_contract_month = dt_maturity.strftime("%y%m")
                amt_strike = exercise_price[idx]
                if sec_name[idx][-1] == 'A':
                    id_instrument = '50etf_' + name_contract_month + '_' + cd_option_type[0] + '_' + str(amt_strike)[
                                                                                                     :6] + '_A'
                else:
                    id_instrument = '50etf_' + name_contract_month + '_' + cd_option_type[0] + '_' + str(amt_strike)[:6]

                dt_listed = listed_date[idx]
                dt_maturity = expire_date[idx]
                dt_exercise = datetime.datetime.strptime(exercise_date[idx], "%Y-%m-%d").date()
                dt_settlement = datetime.datetime.strptime(settlement_date[idx], "%Y-%m-%d").date()
                cd_settle_method = settle_mode[idx].encode('utf-8')
                nbr_multiplier = contract_unit[idx]

                db_row = {'id_instrument': id_instrument,
                          'windcode': windcode,
                          'name_option': name_option,
                          'id_underlying': id_underlying,
                          'windcode_underlying': windcode_underlying,
                          'cd_option_type': cd_option_type,
                          'cd_exercise_type': cd_exercise_type,
                          'amt_strike': amt_strike,
                          'name_contract_month': name_contract_month,
                          'dt_listed': dt_listed,
                          'dt_maturity': dt_maturity,
                          'dt_exercise': dt_exercise,
                          'dt_settlement': dt_settlement,
                          'cd_settle_method': cd_settle_method,
                          'nbr_multiplier': nbr_multiplier,
                          'cd_exchange': cd_exchange,
                          'timestamp': datetime.datetime.today()
                          }
                db_data.append(db_row)
            return db_data

        def wind_options_m(self):
            db_data = []
            name_code = 'm'
            cd_exchange = 'dce'
            data = w.wset("optionfuturescontractbasicinfo", "exchange=DCE;productcode=M;status=trading")
            optionData = data.Data
            optionFlds = data.Fields

            wind_code = optionData[optionFlds.index('wind_code')]
            sec_name = optionData[optionFlds.index('sec_name')]
            option_mark_code = optionData[optionFlds.index('option_mark_code')]
            call_or_put = optionData[optionFlds.index('call_or_put')]
            exercise_mode = optionData[optionFlds.index('exercise_mode')]
            exercise_price = optionData[optionFlds.index('exercise_price')]
            contract_unit = optionData[optionFlds.index('contract_unit')]
            limit_month = optionData[optionFlds.index('limit_month')]
            listed_date = optionData[optionFlds.index('listed_date')]
            expire_date = optionData[optionFlds.index('expire_date')]
            settle_mode = optionData[optionFlds.index('settle_mode')]

            for idx, windcode in enumerate(wind_code):
                windcode = windcode + '.DCE'
                name_option = sec_name[idx].encode('utf-8')
                if call_or_put[idx] == '认购':
                    cd_option_type = 'call'
                elif call_or_put[idx] == '认沽':
                    cd_option_type = 'put'
                else:
                    cd_option_type = 'none'
                    print('error in call_or_put')
                cd_exercise_type = exercise_mode[idx].encode('utf-8')
                name_contract_month = datetime.datetime.strptime(limit_month[idx], "%Y-%m").date().strftime("%y%m")
                amt_strike = exercise_price[idx]
                id_instrument = name_code + '_' + name_contract_month + '_' + cd_option_type[0] + '_' + str(
                    int(amt_strike))
                id_underlying = name_code + '_' + name_contract_month
                windcode_underlying = option_mark_code[idx]
                dt_listed = listed_date[idx]
                dt_maturity = expire_date[idx]
                cd_settle_method = settle_mode[idx].encode('utf-8')
                nbr_multiplier = contract_unit[idx]

                db_row = {'id_instrument': id_instrument,
                          'windcode': windcode,
                          'name_option': name_option,
                          'id_underlying': id_underlying,
                          'windcode_underlying': windcode_underlying,
                          'cd_option_type': cd_option_type,
                          'cd_exercise_type': cd_exercise_type,
                          'amt_strike': amt_strike,
                          'name_contract_month': name_contract_month,
                          'dt_listed': dt_listed,
                          'dt_maturity': dt_maturity,
                          'cd_settle_method': cd_settle_method,
                          'nbr_multiplier': nbr_multiplier,
                          'cd_exchange': cd_exchange,
                          'timestamp': datetime.datetime.today()
                          }
                db_data.append(db_row)
            return db_data

        def wind_options_sr(self):
            db_data = []
            name_code = 'sr'
            cd_exchange = 'czce'
            data = w.wset("optionfuturescontractbasicinfo", "exchange=CZCE;productcode=SR;status=trading")
            optionData = data.Data
            optionFlds = data.Fields

            wind_code = optionData[optionFlds.index('wind_code')]
            sec_name = optionData[optionFlds.index('sec_name')]
            option_mark_code = optionData[optionFlds.index('option_mark_code')]
            call_or_put = optionData[optionFlds.index('call_or_put')]
            exercise_mode = optionData[optionFlds.index('exercise_mode')]
            exercise_price = optionData[optionFlds.index('exercise_price')]
            contract_unit = optionData[optionFlds.index('contract_unit')]
            limit_month = optionData[optionFlds.index('limit_month')]
            listed_date = optionData[optionFlds.index('listed_date')]
            expire_date = optionData[optionFlds.index('expire_date')]
            settle_mode = optionData[optionFlds.index('settle_mode')]

            for idx, windcode in enumerate(wind_code):
                windcode = windcode + '.CZC'
                name_option = sec_name[idx].encode('utf-8')
                if call_or_put[idx] == '认购':
                    cd_option_type = 'call'
                elif call_or_put[idx] == '认沽':
                    cd_option_type = 'put'
                else:
                    cd_option_type = 'none'
                    print('error in call_or_put')
                cd_exercise_type = exercise_mode[idx].encode('utf-8')
                name_contract_month = datetime.datetime.strptime(limit_month[idx], "%Y-%m").date().strftime("%y%m")
                amt_strike = exercise_price[idx]
                id_instrument = name_code + '_' + name_contract_month + '_' + cd_option_type[0] + '_' + str(
                    int(amt_strike))
                id_underlying = name_code + '_' + name_contract_month
                windcode_underlying = option_mark_code[idx]
                dt_listed = listed_date[idx]
                dt_maturity = expire_date[idx]
                cd_settle_method = settle_mode[idx].encode('utf-8')
                nbr_multiplier = contract_unit[idx]

                db_row = {'id_instrument': id_instrument,
                          'windcode': windcode,
                          'name_option': name_option,
                          'id_underlying': id_underlying,
                          'windcode_underlying': windcode_underlying,
                          'cd_option_type': cd_option_type,
                          'cd_exercise_type': cd_exercise_type,
                          'amt_strike': amt_strike,
                          'name_contract_month': name_contract_month,
                          'dt_listed': dt_listed,
                          'dt_maturity': dt_maturity,
                          'cd_settle_method': cd_settle_method,
                          'nbr_multiplier': nbr_multiplier,
                          'cd_exchange': cd_exchange,
                          'timestamp': datetime.datetime.today()
                          }
                db_data.append(db_row)
            return db_data

    class table_index():

        def wind_data_index(self, windcode, date, id_instrument):
            db_data = []
            datasource = 'wind'
            data = w.wsd(windcode, "open,high,low,close,volume,amt",
                         date, date, "")
            df = pd.DataFrame()
            for i, f in enumerate(data.Fields):
                df[f] = data.Data[i]
            df['times'] = data.Times
            df.fillna(0.0)
            for (idx, row) in df.iterrows():
                open_price = row['OPEN']
                dt = row['times']
                high = row['HIGH']
                low = row['LOW']
                close = row['CLOSE']
                volume = row['VOLUME']
                amt = row['AMT']
                if np.isnan(volume): volume = 0.0
                if np.isnan(amt): amt = 0.0
                if np.isnan(low): low = -1.0
                if np.isnan(high): high = -1.0
                if np.isnan(open_price): open_price = -1.0
                db_row = {'dt_date': dt,
                          'id_instrument': id_instrument,
                          'datasource': datasource,
                          'code_instrument': windcode,
                          'amt_close': close,
                          'amt_open': open_price,
                          'amt_high': high,
                          'amt_low': low,
                          'amt_trading_volume': volume,
                          'amt_trading_value': amt,
                          'timestamp': datetime.datetime.today()
                          }
                db_data.append(db_row)
            return db_data

        def wind_data_index_hist(self, windcode, begdate, enddate, id_instrument):
            db_data = []
            datasource = 'wind'
            data = w.wsd(windcode, "open,high,low,close,volume,amt",
                         begdate, enddate, "")
            df = pd.DataFrame()
            for i, f in enumerate(data.Fields):
                df[f] = data.Data[i]
            df['times'] = data.Times
            df.fillna(0.0)
            for (idx, row) in df.iterrows():
                open_price = row['OPEN']
                dt = row['times']
                high = row['HIGH']
                low = row['LOW']
                close = row['CLOSE']
                volume = row['VOLUME']
                amt = row['AMT']
                if volume==None or np.isnan(volume): volume = 0.0
                if amt==None or np.isnan(amt): amt = 0.0
                if low==None or np.isnan(low): low = -1.0
                if high==None or np.isnan(high): high = -1.0
                if open_price==None or np.isnan(open_price): open_price = -1.0
                db_row = {'dt_date': dt,
                          'id_instrument': id_instrument,
                          'datasource': datasource,
                          'code_instrument': windcode,
                          'amt_close': close,
                          'amt_open': open_price,
                          'amt_high': high,
                          'amt_low': low,
                          'amt_trading_volume': volume,
                          'amt_trading_value': amt,
                          'timestamp': datetime.datetime.today()
                          }
                db_data.append(db_row)
            return db_data

    class table_index_intraday():

        def wind_data_equity_index(self, windcode, date, id_instrument):
            db_data = []
            datasource = 'wind'
            data = w.wsi(windcode, "close,volume,amt", date + " 09:00:00", date + " 15:01:00", "Fill=Previous")
            datetimes = data.Times
            prices = data.Data[0]
            volumes = data.Data[1]
            trading_values = data.Data[2]
            for idx, dt in enumerate(datetimes):
                price = prices[idx]
                volume = volumes[idx]
                trading_value = trading_values[idx]
                db_row = {'dt_datetime': dt,
                          'id_instrument': id_instrument,
                          'datasource': datasource,
                          'code_instrument': windcode,
                          'amt_close': price,
                          'amt_trading_volume': volume,
                          'amt_trading_value': trading_value,
                          'timestamp': datetime.datetime.today()
                          }
                db_data.append(db_row)
            return db_data

    class table_option_intraday():

        def wind_data_50etf_option_intraday(self, datestr, df_optionchain_row):
            db_data = []
            datasource = 'wind'
            windcode = df_optionchain_row['windcode']
            id_instrument = df_optionchain_row['id_instrument']
            data = w.wsi(windcode, "close,volume,amt", datestr + " 09:00:00", datestr + " 15:01:00", "Fill=Previous")
            datetimes = data.Times
            errorcode = data.ErrorCode
            print(errorcode)
            try:
                prices = data.Data[0]
                volumes = data.Data[1]
                trading_values = data.Data[2]
                for idx, dt in enumerate(datetimes):
                    price = prices[idx]
                    volume = volumes[idx]
                    trading_value = trading_values[idx]
                    if math.isnan(price): continue
                    if math.isnan(volume): volume = 0.0
                    if math.isnan(trading_value): trading_value = 0.0
                    db_row = {'dt_datetime': dt,
                              'id_instrument': id_instrument,
                              'datasource': datasource,
                              'code_instrument': windcode,
                              'amt_close': price,
                              'amt_trading_volume': volume,
                              'amt_trading_value': trading_value,
                              'timestamp': datetime.datetime.today()
                              }
                    db_data.append(db_row)
            except Exception as e:
                print(e)
                # print(datestr, ' , ', id_instrument)
            return db_data

        def wind_data_50etf_option_intraday2(self, datestr, windcode,id_instrument):
            db_data = []
            datasource = 'wind'
            data = w.wsi(windcode, "close,volume,amt", datestr + " 09:00:00", datestr + " 15:01:00", "Fill=Previous")
            datetimes = data.Times
            try:
                prices = data.Data[0]
                volumes = data.Data[1]
                trading_values = data.Data[2]
                for idx, dt in enumerate(datetimes):
                    price = prices[idx]
                    volume = volumes[idx]
                    trading_value = trading_values[idx]
                    if math.isnan(price): continue
                    if math.isnan(volume): volume = 0.0
                    if math.isnan(trading_value): trading_value = 0.0
                    db_row = {'dt_datetime': dt,
                              'id_instrument': id_instrument,
                              'datasource': datasource,
                              'code_instrument': windcode,
                              'amt_close': price,
                              'amt_trading_volume': volume,
                              'amt_trading_value': trading_value,
                              'timestamp': datetime.datetime.today()
                              }
                    db_data.append(db_row)
            except Exception as e:
                print(e)
                print(datestr, ' , ', id_instrument)
            return db_data

    class table_option_tick():

        def wind_50etf_option_tick(self, datestr, df_optionchain_row):
            db_data = []
            datasource = 'wind'
            windcode = df_optionchain_row['windcode']
            id_instrument = df_optionchain_row['id_instrument']
            tickdata = w.wst(windcode,
                             "last,volume,amt,oi,limit_up,limit_down,ask1,ask2,ask3,ask4,ask5,bid1,bid2,bid3,bid4,bid5",
                             datestr + " 09:25:00", datestr + " 15:01:00", "")
            if tickdata.ErrorCode != 0:
                print('wind get data error ', datestr, ',errorcode : ', tickdata.ErrorCode)
                return []
            df_tickdata = pd.DataFrame()
            for i, f in enumerate(tickdata.Fields):
                df_tickdata[f] = tickdata.Data[i]
            df_tickdata['dt_datetime'] = tickdata.Times
            df_tickdata = df_tickdata.fillna(0.0)
            last_datetime = None
            for (idx, row_tickdata) in df_tickdata.iterrows():
                dt = row_tickdata['dt_datetime']
                dt_datetime = datetime.datetime(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second)
                if dt_datetime == last_datetime: continue
                last_datetime = dt_datetime
                price = row_tickdata['last']
                volume = row_tickdata['volume']
                trading_value = row_tickdata['amount']
                position = row_tickdata['position']
                amt_bid1 = row_tickdata['bid1']
                amt_ask1 = row_tickdata['ask1']
                amt_bid2 = row_tickdata['bid2']
                amt_ask2 = row_tickdata['ask2']
                amt_bid3 = row_tickdata['bid3']
                amt_ask3 = row_tickdata['ask3']
                amt_bid4 = row_tickdata['bid4']
                amt_ask4 = row_tickdata['ask4']
                amt_bid5 = row_tickdata['bid5']
                amt_ask5 = row_tickdata['ask5']
                db_row = {'dt_datetime': dt_datetime,
                          'id_instrument': id_instrument,
                          'datasource': datasource,
                          'code_instrument': windcode,
                          'amt_price': price,
                          'amt_trading_volume': volume,
                          'amt_trading_value': trading_value,
                          'amt_holding_volume': position,
                          'amt_bid1': amt_bid1,
                          'amt_ask1': amt_ask1,
                          'amt_bid2': amt_bid2,
                          'amt_ask2': amt_ask2,
                          'amt_bid3': amt_bid3,
                          'amt_ask3': amt_ask3,
                          'amt_bid4': amt_bid4,
                          'amt_ask4': amt_ask4,
                          'amt_bid5': amt_bid5,
                          'amt_ask5': amt_ask5,
                          'timestamp': datetime.datetime.today()
                          }
                db_data.append(db_row)
            return db_data

    class table_future_tick():

        def wind_index_future_tick(self, datestr, id_instrument, windcode):
            db_data = []
            datasource = 'wind'
            tickdata = w.wst(windcode,
                             "last,volume,amt,oi,limit_up,limit_down,ask1,ask2,ask3,ask4,ask5,"
                             "bid1,bid2,bid3,bid4,bid5", datestr + " 09:25:00", datestr + " 15:01:00", "")
            if tickdata.ErrorCode != 0:
                print('wind get data error ', datestr, ',errorcode : ', tickdata.ErrorCode)
                return []
            df_tickdata = pd.DataFrame()
            for i, f in enumerate(tickdata.Fields):
                df_tickdata[f] = tickdata.Data[i]
            df_tickdata['dt_datetime'] = tickdata.Times
            df_tickdata = df_tickdata.fillna(0.0)
            last_datetime = None
            for (idx, row_tickdata) in df_tickdata.iterrows():
                dt = row_tickdata['dt_datetime']
                dt_datetime = datetime.datetime(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second)
                if dt_datetime == last_datetime: continue
                last_datetime = dt_datetime
                price = row_tickdata['last']
                volume = row_tickdata['volume']
                trading_value = row_tickdata['amount']
                position = row_tickdata['position']
                amt_bid1 = row_tickdata['bid1']
                amt_ask1 = row_tickdata['ask1']
                amt_bid2 = row_tickdata['bid2']
                amt_ask2 = row_tickdata['ask2']
                amt_bid3 = row_tickdata['bid3']
                amt_ask3 = row_tickdata['ask3']
                amt_bid4 = row_tickdata['bid4']
                amt_ask4 = row_tickdata['ask4']
                amt_bid5 = row_tickdata['bid5']
                amt_ask5 = row_tickdata['ask5']
                db_row = {'dt_datetime': dt_datetime,
                          'id_instrument': id_instrument,
                          'datasource': datasource,
                          'code_instrument': windcode,
                          'amt_price': price,
                          'amt_trading_volume': volume,
                          'amt_trading_value': trading_value,
                          'amt_holding_volume': position,
                          'amt_bid1': amt_bid1,
                          'amt_ask1': amt_ask1,
                          'amt_bid2': amt_bid2,
                          'amt_ask2': amt_ask2,
                          'amt_bid3': amt_bid3,
                          'amt_ask3': amt_ask3,
                          'amt_bid4': amt_bid4,
                          'amt_ask4': amt_ask4,
                          'amt_bid5': amt_bid5,
                          'amt_ask5': amt_ask5,
                          'timestamp': datetime.datetime.today()
                          }
                db_data.append(db_row)
            return db_data

    class table_future_positions():

        def dce_data(self, dt, name_code, data_list):
            db_data = []
            types = ['trading_volume', 'holding_volume_buy', 'holding_volume_sell']
            type_index = ['成交量', '持买单量', '持卖单量']
            for i, data in enumerate(data_list):
                for column in data.columns.values:
                    product = data[column]
                    dt_date = dt
                    id_instrument = name_code + '_all'
                    cd_positions_type = types[i]
                    nbr_rank = int(product.loc['名次'])
                    name_company = product.loc['会员简称'].replace(' ', '').encode('utf-8')
                    amt_volume = product.loc[type_index[i]].replace(',', '')
                    amt_difference = product.loc['增减'].replace(',', '')
                    db_row = {'dt_date': dt_date,
                              'cd_positions_type': cd_positions_type,
                              'id_instrument': id_instrument,
                              'nbr_rank': nbr_rank,
                              'name_company': name_company,
                              'amt_volume': amt_volume,
                              'amt_difference': amt_difference,
                              'cd_exchange': 'dce',
                              'timestamp': datetime.datetime.today()
                              }
                    db_data.append(db_row)
            return db_data

        def sfe_data(self, dt, data):
            # types = ['trading_volume', 'holding_volume_buy', 'holding_volume_sell']
            data_dict = data['o_cursor']
            db_data = []
            for dict in data_dict:
                instrumentid = dict['INSTRUMENTID'].replace(' ', '')
                try:
                    if instrumentid[-3:] == 'all':
                        id_instrument = instrumentid[0:-3] + '_' + 'all'
                    else:
                        name_code = instrumentid[0:instrumentid.index('1')]
                        contractmonth = instrumentid[-4:]
                        id_instrument = name_code + '_' + contractmonth
                except:
                    print(instrumentid)
                    continue
                dt_date = dt

                cd_positions_type = 'trading_volume'
                nbr_rank = dict['RANK']
                name_company = dict['PARTICIPANTABBR1'].encode('utf-8')
                amt_volume = dict['CJ1']
                amt_difference = dict['CJ1_CHG']
                if amt_volume == '': amt_volume = 0.0
                if amt_difference == '': amt_difference = 0.0
                db_row = {'dt_date': dt_date,
                          'cd_positions_type': cd_positions_type,
                          'id_instrument': id_instrument,
                          'nbr_rank': nbr_rank,
                          'name_company': name_company,
                          'amt_volume': amt_volume,
                          'amt_difference': amt_difference,
                          'cd_exchange': 'sfe',
                          'timestamp': datetime.datetime.today()
                          }
                db_data.append(db_row)
                cd_positions_type = 'holding_volume_buy'
                # nbr_rank = dict['RANK']
                name_company = dict['PARTICIPANTABBR2'].encode('utf-8')
                amt_volume = dict['CJ2']
                amt_difference = dict['CJ2_CHG']
                if amt_volume == '': amt_volume = 0.0
                if amt_difference == '': amt_difference = 0.0
                db_row = {'dt_date': dt_date,
                          'cd_positions_type': cd_positions_type,
                          'id_instrument': id_instrument,
                          'nbr_rank': nbr_rank,
                          'name_company': name_company,
                          'amt_volume': amt_volume,
                          'amt_difference': amt_difference,
                          'cd_exchange': 'sfe',
                          'timestamp': datetime.datetime.today()
                          }
                db_data.append(db_row)
                cd_positions_type = 'holding_volume_sell'
                # nbr_rank = dict['RANK']
                name_company = dict['PARTICIPANTABBR3'].encode('utf-8')
                amt_volume = dict['CJ3']
                amt_difference = dict['CJ3_CHG']
                if amt_volume == '': amt_volume = 0.0
                if amt_difference == '': amt_difference = 0.0
                db_row = {'dt_date': dt_date,
                          'cd_positions_type': cd_positions_type,
                          'id_instrument': id_instrument.lower(),
                          'nbr_rank': nbr_rank,
                          'name_company': name_company,
                          'amt_volume': amt_volume,
                          'amt_difference': amt_difference,
                          'cd_exchange': 'sfe',
                          'timestamp': datetime.datetime.today()
                          }
                db_data.append(db_row)
            return db_data
