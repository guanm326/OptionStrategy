import pandas as pd
from sqlalchemy import *
from sqlalchemy.orm import sessionmaker
from data_access.db_tables import DataBaseTables as dbt
from back_test.bkt_util import BktUtil


def get_eventsdata(start_date, end_date,flag_impact):
    engine = create_engine('mysql+pymysql://guest:passw0rd@101.132.148.152/mktdata', echo=False)
    Session = sessionmaker(bind=engine)
    sess = Session()
    metadata = MetaData(engine)
    events = Table('events', metadata, autoload=True)
    query = sess.query(events.c.id_event, events.c.name_event, events.c.dt_impact_beg,
                       events.c.cd_trade_direction, events.c.dt_test,events.c.dt_test2,
                       events.c.dt_impact_end, events.c.dt_vol_peak,events.c.cd_open_position_time,
                       events.c.cd_close_position_time) \
        .filter(events.c.dt_date >= start_date) \
        .filter(events.c.dt_date <= end_date) \
        .filter(events.c.flag_impact == flag_impact)\
        # .filter(events.c.cd_occurrence == 'e')
    df_event = pd.read_sql(query.statement, query.session.bind)
    return df_event


def get_50etf_mktdata(start_date, end_date):
    engine = create_engine('mysql+pymysql://guest:passw0rd@101.132.148.152/mktdata', echo=False)
    Session = sessionmaker(bind=engine)
    sess = Session()
    Index_mkt = dbt.IndexMkt

    query_etf = sess.query(Index_mkt.dt_date, Index_mkt.amt_close, Index_mkt.id_instrument) \
        .filter(Index_mkt.dt_date >= start_date).filter(Index_mkt.dt_date <= end_date) \
        .filter(Index_mkt.id_instrument == 'index_50etf')
    df = pd.read_sql(query_etf.statement, query_etf.session.bind)
    return df


def get_50option_mktdata(start_date, end_date):
    engine = create_engine('mysql+pymysql://guest:passw0rd@101.132.148.152/mktdata', echo=False)
    Session = sessionmaker(bind=engine)
    sess = Session()
    Index_mkt = dbt.IndexMkt
    Option_mkt = dbt.OptionMkt
    options = dbt.Options
    util = BktUtil()

    query_mkt = sess.query(Option_mkt.dt_date, Option_mkt.id_instrument, Option_mkt.code_instrument,
                           Option_mkt.amt_open,
                           Option_mkt.amt_close, Option_mkt.amt_settlement, Option_mkt.amt_last_settlement,
                           Option_mkt.amt_trading_volume, Option_mkt.pct_implied_vol
                           ) \
        .filter(Option_mkt.dt_date >= start_date).filter(Option_mkt.dt_date <= end_date) \
        .filter(Option_mkt.datasource == 'wind')

    query_option = sess.query(options.id_instrument, options.cd_option_type, options.amt_strike,
                              options.dt_maturity, options.nbr_multiplier) \
        .filter(and_(options.dt_listed <= end_date, options.dt_maturity >= start_date))

    query_etf = sess.query(Index_mkt.dt_date, Index_mkt.amt_close,
                           Index_mkt.id_instrument.label(util.col_id_underlying)) \
        .filter(Index_mkt.dt_date >= start_date).filter(Index_mkt.dt_date <= end_date) \
        .filter(Index_mkt.id_instrument == 'index_50etf')

    df_mkt = pd.read_sql(query_mkt.statement, query_mkt.session.bind)
    df_contract = pd.read_sql(query_option.statement, query_option.session.bind)
    df_50etf = pd.read_sql(query_etf.statement, query_etf.session.bind).rename(
        columns={'amt_close': util.col_underlying_price})
    df_option = df_mkt.join(df_contract.set_index('id_instrument'), how='left', on='id_instrument')

    df_option_metrics = df_option.join(df_50etf.set_index('dt_date'), how='left', on='dt_date')
    return df_option_metrics


def get_50option_mktdata2(start_date, end_date):
    engine = create_engine('mysql+pymysql://guest:passw0rd@101.132.148.152/mktdata', echo=False)
    Session = sessionmaker(bind=engine)
    sess = Session()
    engine2 = create_engine('mysql+pymysql://guest:passw0rd@101.132.148.152/metrics', echo=False)
    Session2 = sessionmaker(bind=engine2)
    sess2 = Session2()
    Index_mkt = dbt.IndexMkt
    Option_mkt = dbt.OptionMktGolden
    options = dbt.Options
    util = BktUtil()

    query_mkt = sess2.query(Option_mkt.dt_date, Option_mkt.id_instrument, Option_mkt.code_instrument,
                            Option_mkt.amt_open,
                            Option_mkt.amt_close, Option_mkt.amt_settlement, Option_mkt.amt_last_settlement,
                            Option_mkt.amt_trading_volume, Option_mkt.pct_implied_vol,
                            Option_mkt.amt_afternoon_close_15min, Option_mkt.amt_afternoon_open_15min,
                            Option_mkt.amt_morning_close_15min, Option_mkt.amt_morning_open_15min,
                            Option_mkt.amt_daily_avg,Option_mkt.amt_afternoon_avg,Option_mkt.amt_morning_avg
                            ) \
        .filter(Option_mkt.dt_date >= start_date).filter(Option_mkt.dt_date <= end_date) \
        .filter(Option_mkt.datasource == 'wind')

    query_option = sess.query(options.id_instrument, options.cd_option_type, options.amt_strike,
                              options.dt_maturity, options.nbr_multiplier) \
        .filter(and_(options.dt_listed <= end_date, options.dt_maturity >= start_date))

    query_etf = sess.query(Index_mkt.dt_date, Index_mkt.amt_close,Index_mkt.amt_open,
                           Index_mkt.id_instrument.label(util.col_id_underlying),
                           ) \
        .filter(Index_mkt.dt_date >= start_date).filter(Index_mkt.dt_date <= end_date) \
        .filter(Index_mkt.id_instrument == 'index_50etf')

    df_mkt = pd.read_sql(query_mkt.statement, query_mkt.session.bind)
    df_contract = pd.read_sql(query_option.statement, query_option.session.bind)
    df_50etf = pd.read_sql(query_etf.statement, query_etf.session.bind).rename(
        columns={'amt_close': util.col_underlying_price,'amt_open':util.col_underlying_open_price})
    df_option = df_mkt.join(df_contract.set_index('id_instrument'), how='left', on='id_instrument')

    df_option_metrics = df_option.join(df_50etf.set_index('dt_date'), how='left', on='dt_date')
    return df_option_metrics


def get_comoption_mktdata(start_date, end_date, name_code):
    engine = create_engine('mysql+pymysql://guest:passw0rd@101.132.148.152/mktdata', echo=False)
    Session = sessionmaker(bind=engine)
    sess = Session()
    util = BktUtil()

    Future_mkt = dbt.FutureMkt
    Option_mkt = dbt.OptionMkt
    options = dbt.Options
    query_mkt = sess.query(Option_mkt.dt_date, Option_mkt.id_instrument, Option_mkt.id_underlying,
                           Option_mkt.code_instrument, Option_mkt.amt_close, Option_mkt.amt_settlement,
                           Option_mkt.amt_last_settlement, Option_mkt.amt_trading_volume,
                           Option_mkt.pct_implied_vol
                           ) \
        .filter(Option_mkt.dt_date >= start_date).filter(Option_mkt.dt_date <= end_date) \
        .filter(Option_mkt.name_code == name_code).filter(Option_mkt.flag_night != 1)

    query_option = sess.query(options.id_instrument, options.cd_option_type, options.amt_strike,
                              options.dt_maturity, options.nbr_multiplier) \
        .filter(and_(options.dt_listed <= end_date, options.dt_maturity >= start_date))

    query_srf = sess.query(Future_mkt.dt_date, Future_mkt.id_instrument.label(util.col_id_underlying),
                           Future_mkt.amt_settlement.label(util.col_underlying_price)) \
        .filter(Future_mkt.dt_date >= start_date).filter(Future_mkt.dt_date <= end_date) \
        .filter(Future_mkt.name_code == name_code).filter(Future_mkt.flag_night != 1)

    df_srf = pd.read_sql(query_srf.statement, query_srf.session.bind)

    df_mkt = pd.read_sql(query_mkt.statement, query_mkt.session.bind)
    df_contract = pd.read_sql(query_option.statement, query_option.session.bind)

    df_option = df_mkt.join(df_contract.set_index('id_instrument'), how='left', on='id_instrument')
    df_option_metrics = pd.merge(df_option, df_srf, how='left', on=['dt_date', 'id_underlying'], suffixes=['', '_r'])
    return df_option_metrics
