import datetime
from Utilities.calculate import calculate_histvol
from regular_reports.report_util import *
from data_access import get_data
from back_test.model import constant as c
from back_test.model.base_option_set import BaseOptionSet
from OptionStrategyLib.VolatilityModel.historical_volatility import HistoricalVolatilityModels as Histvol


def iv_at_the_money(dt_date, dt_last, name_code):
    dict_iv_call = {}
    dict_iv_put = {}
    df_metrics = get_data.get_comoption_mktdata(dt_last, dt_date, name_code)
    optionset = BaseOptionSet(df_metrics,rf=0.0)
    optionset.init()
    dt_maturity = optionset.select_maturity_date(0, 0)
    call_list, put_list = optionset.get_options_list_by_moneyness_mthd1(0, dt_maturity)
    atm_call = optionset.select_higher_volume(call_list)
    atm_put = optionset.select_higher_volume(put_list)
    iv_call = atm_call.get_implied_vol()*100
    iv_put = atm_put.get_implied_vol()*100
    dict_iv_call.update({dt_last: iv_call})
    dict_iv_put.update({dt_last: iv_put})
    optionset.go_to(dt_date)
    dt_maturity = optionset.select_maturity_date(0, 0)
    call_list, put_list = optionset.get_options_list_by_moneyness_mthd1(0, dt_maturity)
    atm_call = optionset.select_higher_volume(call_list)
    atm_put = optionset.select_higher_volume(put_list)
    iv_call = atm_call.get_implied_vol()*100
    iv_put = atm_put.get_implied_vol()*100
    dict_iv_call.update({dt_date: iv_call})
    dict_iv_put.update({dt_date: iv_put})
    return dict_iv_call, dict_iv_put


def iv_volume_weighted(dt_date, dt_last, name_code):
    dict_iv = {}
    df_metrics = get_data.get_comoption_mktdata(dt_last, dt_date, name_code)
    optionset = BaseOptionSet(df_metrics)
    optionset.init()
    dt_maturity = optionset.select_maturity_date(0, 0)
    iv_volume_weighted = optionset.get_volume_weighted_iv(dt_maturity)*100
    dict_iv.update({dt_last: iv_volume_weighted})
    optionset.go_to(dt_date)
    dt_maturity = optionset.select_maturity_date(0, 0)
    iv_volume_weighted = optionset.get_volume_weighted_iv(dt_maturity)*100
    dict_iv.update({dt_date: iv_volume_weighted})
    return dict_iv

def iv_htbr(dt_date, dt_last, name_code):
    dict_iv = {}
    df_metrics = get_data.get_comoption_mktdata(dt_last, dt_date, name_code)
    optionset = BaseOptionSet(df_metrics,rf=0)
    optionset.init()
    dt_maturity = optionset.select_maturity_date(0, 0)
    iv_curve_htbr = optionset.get_implied_vol_curves_htbr(dt_maturity)
    call_list, put_list = optionset.get_options_list_by_moneyness_mthd1(0, dt_maturity)
    atm_k = call_list[0].applicable_strike()
    iv = iv_curve_htbr[iv_curve_htbr[c.Util.AMT_APPLICABLE_STRIKE] == atm_k][c.Util.PCT_IV_PUT_BY_HTBR].values[0]*100
    dict_iv.update({dt_last: iv})
    optionset.go_to(dt_date)
    dt_maturity = optionset.select_maturity_date(0, 0)
    iv_curve_htbr = optionset.get_implied_vol_curves_htbr(dt_maturity)
    call_list, put_list = optionset.get_options_list_by_moneyness_mthd1(0, dt_maturity)
    atm_k = call_list[0].applicable_strike()
    iv = iv_curve_htbr[iv_curve_htbr[c.Util.AMT_APPLICABLE_STRIKE] == atm_k][c.Util.PCT_IV_PUT_BY_HTBR].values[0]*100
    dict_iv.update({dt_date: iv})
    return dict_iv



def get_mktdata_future_c1(start_date, end_date, name_code):
    table_f = admin.table_futures_mktdata()
    query = admin.session_mktdata().query(table_f.c.dt_date, table_f.c.id_instrument,
                                          table_f.c.amt_close, table_f.c.amt_trading_volume). \
        filter((table_f.c.dt_date >= start_date) & (table_f.c.dt_date <= end_date)). \
        filter(table_f.c.name_code == name_code).filter(table_f.c.flag_night != 1)
    df = pd.read_sql(query.statement, query.session.bind)
    df = df[df['id_instrument'].str.contains("_")]
    df = df.sort_values(by=['dt_date', 'amt_trading_volume'], ascending=False)
    df_rs = df.drop_duplicates(subset=['dt_date']).sort_values(by='dt_date', ascending=True).reset_index(drop=True)
    return df_rs


def get_mktdata_future(table_future, id_instrument, dt_start, dt_end):
    query = admin.session_mktdata().query(table_future.c.dt_date, table_future.c.id_instrument,
                                          table_future.c.amt_close, table_future.c.amt_trading_volume,
                                          table_future.c.amt_settlement) \
        .filter(table_future.c.dt_date >= dt_start).filter(table_future.c.dt_date <= dt_end) \
        .filter(table_future.c.id_instrument == id_instrument) \
        .filter(table_future.c.flag_night != 1)
    df = pd.read_sql(query.statement, query.session.bind)
    return df


def get_volume_option(table_option, id_underlying, dt_start, dt_end):
    query = admin.session_mktdata().query(table_option.c.dt_date, table_option.c.id_underlying,
                                          table_option.c.amt_strike, table_option.c.cd_option_type,
                                          func.sum(table_option.c.amt_holding_volume).label('total_holding_volume'),
                                          func.sum(table_option.c.amt_trading_volume).label('total_trading_volume')
                                          ) \
        .filter(table_option.c.dt_date >= dt_start).filter(table_option.c.dt_date <= dt_end) \
        .filter(table_option.c.id_underlying == id_underlying).filter(table_option.c.flag_night != 1) \
        .group_by(table_option.c.dt_date, table_option.c.amt_strike, table_option.c.cd_option_type)
    df = pd.read_sql(query.statement, query.session.bind)
    return df


def get_volume_groupby_id_type(table_option, namecode, dt_start, dt_end):
    query = admin.session_mktdata().query(table_option.c.dt_date, table_option.c.cd_option_type,
                                          table_option.c.id_underlying,
                                          func.sum(table_option.c.amt_holding_volume).label('total_holding_volume'),
                                          func.sum(table_option.c.amt_trading_volume).label('total_trading_volume')
                                          ) \
        .filter(table_option.c.dt_date >= dt_start).filter(table_option.c.dt_date <= dt_end) \
        .filter(table_option.c.name_code == namecode).filter(table_option.c.flag_night != 1)  \
        .group_by(table_option.c.cd_option_type, table_option.c.dt_date, table_option.c.id_underlying)
    df = pd.read_sql(query.statement, query.session.bind)
    return df


def get_volume_groupby_id_option(table_option, namecode, dt_start, dt_end):
    query = admin.session_mktdata().query(table_option.c.dt_date, table_option.c.id_underlying,
                                          func.sum(table_option.c.amt_holding_volume).label('total_holding_volume'),
                                          func.sum(table_option.c.amt_trading_volume).label('total_trading_volume')
                                          ) \
        .filter(table_option.c.dt_date >= dt_start).filter(table_option.c.dt_date <= dt_end) \
        .filter(table_option.c.name_code == namecode).filter(table_option.c.flag_night != 1)  \
        .group_by(table_option.c.dt_date, table_option.c.id_underlying)
    df = pd.read_sql(query.statement, query.session.bind)
    return df


def get_volume_groupby_id_future(table_future, namecode, dt_start, dt_end):
    query = admin.session_mktdata().query(table_future.c.dt_date, table_future.c.id_instrument,
                                          func.sum(table_future.c.amt_holding_volume).label('total_holding_volume'),
                                          func.sum(table_future.c.amt_trading_volume).label('total_trading_volume')
                                          ) \
        .filter(table_future.c.dt_date >= dt_start).filter(table_future.c.dt_date <= dt_end) \
        .filter(table_future.c.name_code == namecode).filter(table_future.c.flag_night != 1)  \
        .group_by(table_future.c.dt_date, table_future.c.id_instrument)
    df = pd.read_sql(query.statement, query.session.bind)
    return df


def fun_report_compare(d1, d2):
    if d1 > d2:
        return '增加'
    elif d1 < d2:
        return '减少'
    else:
        return '持平'


def fun_report_compare2(d1, d2):
    if abs(d1 - d2) / d2 <= 0.02:
        return '持平'
    elif d1 > d2:
        return '有所提升'
    else:
        return '有所下降'


def fun_report_compare3(d1, d2):
    if abs(d1 - d2) / d2 <= 0.02:
        return '基本持平'
    elif d1 > d2:
        return '偏高'
    else:
        return '偏低'


def fun_report_compare4(d1, d2):
    if d1 == d2:
        return '亦'
    else:
        return ''


def fun_report_namecode(namecode):
    if namecode == 'm':
        return '豆粕'
    elif namecode == 'sr':
        return '白糖'
    else:
        return 'NAN'


# Eval Settings and Data
dt_date = datetime.date(2018, 10, 19)  # Set as Friday
dt_yesterday = datetime.date(2018, 10, 12) # last friday

# Eval Settings and Data

dt_start = datetime.date(2018, 1, 1)
dict_core_underlying = {}
text = ''
for namecode in ['m', 'sr']:
    str_trading_volume = 'total_trading_volume'
    str_holding_volume = 'total_holding_volume'
    str_id_underlying = 'id_underlying'
    df_volume_groupby = get_volume_groupby_id_option(admin.table_options_mktdata(), namecode, dt_start=dt_date,
                                                     dt_end=dt_date). \
        sort_values(by='total_trading_volume', ascending=False).reset_index(drop=True)
    df_volume_groupby_yeaterday = get_volume_groupby_id_option(admin.table_options_mktdata(), namecode,
                                                               dt_start=dt_yesterday,
                                                               dt_end=dt_yesterday). \
        sort_values(by='total_trading_volume', ascending=False).reset_index(drop=True)
    df_volume_groupby_id_type = get_volume_groupby_id_type(admin.table_options_mktdata(), namecode,
                                                           dt_start=dt_yesterday, dt_end=dt_date)
    id_c1 = df_volume_groupby.loc[0, 'id_underlying']
    id_c2 = df_volume_groupby.loc[1, 'id_underlying']
    dict_core_underlying.update({namecode: id_c1})
    df_c1 = get_volume_option(admin.table_options_mktdata(), id_c1, dt_date, dt_date)
    df_c1_call = df_c1[df_c1['cd_option_type'] == 'call'].sort_values(by=str_holding_volume,
                                                                      ascending=False).reset_index(
        drop=True)
    df_c1_put = df_c1[df_c1['cd_option_type'] == 'put'].sort_values(by=str_holding_volume, ascending=False).reset_index(
        drop=True)

    tradevolume_c1_today = df_volume_groupby.loc[0, 'total_trading_volume']
    holdvolume_c1_today = df_volume_groupby.loc[0, 'total_holding_volume']
    tradevolume_c1_yeaterday = \
        df_volume_groupby_yeaterday[df_volume_groupby_id_type['id_underlying'] == id_c1][str_trading_volume].values[0]
    holdvolume_c1_yeaterday = \
        df_volume_groupby_yeaterday[df_volume_groupby_id_type['id_underlying'] == id_c1][str_holding_volume].values[0]

    tradevolume_c2_today = df_volume_groupby.loc[2, str_trading_volume]
    holdvolume_c2_today = df_volume_groupby.loc[2, str_holding_volume]

    tradevolume_c1_c_today = df_volume_groupby_id_type[(df_volume_groupby_id_type['dt_date'] == dt_date) &
                                                       (df_volume_groupby_id_type['cd_option_type'] == 'call') &
                                                       (df_volume_groupby_id_type['id_underlying'] == id_c1)][
        str_trading_volume].values[0]
    tradevolume_c1_p_today = df_volume_groupby_id_type[(df_volume_groupby_id_type['dt_date'] == dt_date) &
                                                       (df_volume_groupby_id_type['cd_option_type'] == 'put') &
                                                       (df_volume_groupby_id_type['id_underlying'] == id_c1)][
        str_trading_volume].values[0]
    holdvolume_c1_c_today = df_volume_groupby_id_type[(df_volume_groupby_id_type['dt_date'] == dt_date) &
                                                      (df_volume_groupby_id_type['cd_option_type'] == 'call') &
                                                      (df_volume_groupby_id_type['id_underlying'] == id_c1)][
        str_holding_volume].values[0]
    holdvolume_c1_p_today = df_volume_groupby_id_type[(df_volume_groupby_id_type['dt_date'] == dt_date) &
                                                      (df_volume_groupby_id_type['cd_option_type'] == 'put') &
                                                      (df_volume_groupby_id_type['id_underlying'] == id_c1)][
        str_holding_volume].values[0]
    tradevolume_c2_c_today = df_volume_groupby_id_type[(df_volume_groupby_id_type['dt_date'] == dt_date) &
                                                       (df_volume_groupby_id_type['cd_option_type'] == 'call') &
                                                       (df_volume_groupby_id_type['id_underlying'] == id_c2)][
        str_trading_volume].values[0]
    tradevolume_c2_p_today = df_volume_groupby_id_type[(df_volume_groupby_id_type['dt_date'] == dt_date) &
                                                       (df_volume_groupby_id_type['cd_option_type'] == 'put') &
                                                       (df_volume_groupby_id_type['id_underlying'] == id_c2)][
        str_trading_volume].values[0]

    max_hold_amt_call_1st = df_c1_call.loc[0, str_holding_volume]
    max_hold_amt_put_1st = df_c1_put.loc[0, str_holding_volume]
    max_hold_k_call_1st = df_c1_call.loc[0, 'amt_strike']
    max_hold_k_put_1st = df_c1_put.loc[0, 'amt_strike']
    max_hold_amt_call_2nd = df_c1_call.loc[1, str_holding_volume]
    max_hold_amt_put_2nd = df_c1_put.loc[1, str_holding_volume]
    max_hold_k_call_2nd = df_c1_call.loc[1, 'amt_strike']
    max_hold_k_put_2nd = df_c1_put.loc[1, 'amt_strike']

    # refer here http://www.runoob.com/python/att-string-format.html for format usage
    text_1 = '{}年{}月{}日，{}期权{}合约总成交量为{:.0f}手，较前一周{}{:.0f}手，总持仓量为{:.0f}手，较前一周{}{:.0f}手。' \
             '其中，看涨期权总成交量为{:.0f}手，看跌期权总成交量为{:.0f}手，成交量认沽认购比（PCR）为{:.2f}，' \
             '看涨期权总持仓量为{:.0f}手,看跌期权总持仓量为{:.0f}手，' \
             '持仓量认沽认购比（PCR）为{:.2f}。此外{}合约当日看涨与看跌合约总成交{:.0f}手, 总持仓为{:.0f}手。' \
             '最大持仓点位方面，{}合约看跌期权最大持仓对应行权价{:.0f}点，其次为{:.0f}点，持仓量分别为{:.0f}与{:.0f}手，' \
             '看涨期权最大持仓点位为{:.0f}点，其次为{:.0f}点，持仓量分别为{:.0f}与{:.0f}手。\n \n'.format(
        dt_date.year,
        dt_date.month,
        dt_date.day,
        fun_report_namecode(namecode),
        id_c1[-4:],
        tradevolume_c1_today,
        fun_report_compare(tradevolume_c1_today, tradevolume_c1_yeaterday),
        abs(tradevolume_c1_today - tradevolume_c1_yeaterday),
        holdvolume_c1_today,
        fun_report_compare(holdvolume_c1_today, holdvolume_c1_yeaterday),
        abs(holdvolume_c1_today - holdvolume_c1_yeaterday),
        tradevolume_c1_c_today,
        tradevolume_c1_p_today,
        tradevolume_c1_p_today / tradevolume_c1_c_today,
        holdvolume_c1_c_today,
        holdvolume_c1_p_today,
        holdvolume_c1_p_today / holdvolume_c1_c_today,
        id_c2[-4:],
        tradevolume_c2_today,
        holdvolume_c2_today,
        id_c1[-4:],
        max_hold_k_put_1st,
        max_hold_k_put_2nd,
        max_hold_amt_put_1st,
        max_hold_amt_put_2nd,
        max_hold_k_call_1st,
        max_hold_k_call_2nd,
        max_hold_amt_call_1st,
        max_hold_amt_call_2nd,
    )
    text += text_1

for namecode in['m','sr']:
    m_id_c1 = dict_core_underlying[namecode]
    # m_df_future_c1 = get_mktdata_future_c1(dt_start, dt_date, namecode)
    m_df_future_c1 = get_data.get_future_c1_by_option_daily(dt_start, dt_date, namecode, min_holding=5)
    # m_df_future = get_mktdata_future(admin.table_futures_mktdata(), m_id_c1, dt_yesterday, dt_date)
    m_dict_iv_call, m_dict_iv_put = iv_at_the_money(dt_date, dt_yesterday, namecode)
    m_iv_call_today = m_dict_iv_call[dt_date]
    m_iv_put_today = m_dict_iv_put[dt_date]
    m_iv_call_yesterday = m_dict_iv_call[dt_yesterday]
    m_iv_put_yesterday = m_dict_iv_put[dt_yesterday]
    m_df_future_c1['hist_60-1'] = calculate_histvol(m_df_future_c1['amt_close'], 60)
    m_df_future_c1['hist_60-2'] = Histvol.hist_vol(m_df_future_c1['amt_close'], 60)
    m_hisvol_1M = list(calculate_histvol(m_df_future_c1['amt_close'], 20))[-1] * 100
    m_hisvol_3M = list(calculate_histvol(m_df_future_c1['amt_close'], 60))[-1] * 100
    dict_iv = iv_htbr(dt_date, dt_yesterday, namecode)
    iv_today = dict_iv[dt_date]
    iv_last = dict_iv[dt_yesterday]

    text_2 = '隐含波动率方面，{}期权{}月合约隐含波动率整体{}，其中，看跌期权平值合约隐含波动率为{:.2f}%，' \
             '较前一周({:.2f}%){}约{:.1f}%，' \
             '看涨期权平值合约隐含波动率为{:.2f}%，较前一周({:.2f}%){}约{:.1f}%。' \
             '从认沽认购平价隐含波动率来看，{}期权隐含波动率为{:.2f}%，前一周该值为{:.2f}%，{}{:.2f}%。' \
             '期货主力合约近1M历史波动率为{:.2f}%，近3M历史波动率为{:.2f}%，' \
             '平值期权隐含波动率较近1M历史波动率{}，较近3M历史波动率{}{}。'\
             '\n \n'.format(
        fun_report_namecode(namecode),
        m_id_c1[-1],
        fun_report_compare2(m_iv_call_today + m_iv_put_today, m_iv_call_yesterday + m_iv_put_yesterday),
        m_iv_put_today,
        m_iv_put_yesterday,
        fun_report_compare(m_iv_put_today, m_iv_put_yesterday),
        abs(m_iv_put_today - m_iv_put_yesterday),
        m_iv_call_today,
        m_iv_call_yesterday,
        fun_report_compare(m_iv_call_today, m_iv_call_yesterday),
        abs(m_iv_call_today - m_iv_call_yesterday),
        fun_report_namecode(namecode),
        iv_today,
        iv_last,
        fun_report_compare(iv_today, iv_last),
        abs(iv_today - iv_last),
        m_hisvol_1M,
        m_hisvol_3M,
        fun_report_compare3((m_iv_call_today + m_iv_put_today) / 2.0, m_hisvol_1M),
        fun_report_compare4(fun_report_compare3((m_iv_call_today + m_iv_put_today) / 2.0, m_hisvol_1M),
                            fun_report_compare3((m_iv_call_today + m_iv_put_today) / 2.0, m_hisvol_3M)),
        fun_report_compare3((m_iv_call_today + m_iv_put_today) / 2.0, m_hisvol_3M),
    )
    text += text_2
print(text)

with open("../data/morning_report.txt", "w") as text_file:
    text_file.write(text)
