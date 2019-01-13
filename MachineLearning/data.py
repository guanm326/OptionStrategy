import pandas as pd
from Utilities import admin_util as admin

def get_index_mktdata(start_date, end_date, id_index):
    Index_mkt = admin.table_indexes_mktdata()
    query_etf = admin.session_mktdata().query(Index_mkt.c.dt_date, Index_mkt.c.amt_close, Index_mkt.c.amt_open,
                                              Index_mkt.c.id_instrument, Index_mkt.c.amt_high, Index_mkt.c.amt_low,
                                              Index_mkt.c.amt_trading_volume, Index_mkt.c.amt_trading_value) \
        .filter(Index_mkt.c.dt_date >= start_date).filter(Index_mkt.c.dt_date <= end_date) \
        .filter(Index_mkt.c.id_instrument == id_index)
    df_index = pd.read_sql(query_etf.statement, query_etf.session.bind)
    return df_index

def get_index_intraday(start_date, end_date, id_index):
    Index = admin.table_index_mktdata_intraday()
    query = admin.session_intraday().query(Index.c.dt_datetime,Index.c.dt_date, Index.c.id_instrument, Index.c.amt_close,
                                           Index.c.amt_trading_volume, Index.c.amt_trading_value) \
        .filter(Index.c.dt_datetime >= start_date).filter(Index.c.dt_datetime <= end_date) \
        .filter(Index.c.id_instrument == id_index)
    df = pd.read_sql(query.statement, query.session.bind)
    return df