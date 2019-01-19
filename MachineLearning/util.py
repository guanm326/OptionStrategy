import numpy as np
import math
import pandas as pd


class Util:
    """database column names"""
    # basic
    DT_DATE = 'dt_date'
    DT_DATETIME = 'dt_datetime'
    CODE_INSTRUMENT = 'code_instrument'
    ID_INSTRUMENT = 'id_instrument'
    ID_FUTURE = 'id_future'

    # option
    DT_MATURITY = 'dt_maturity'
    ID_UNDERLYING = 'id_underlying'
    CD_OPTION_TYPE = 'cd_option_type'
    NAME_CONTRACT_MONTH = 'name_contract_month'
    AMT_STRIKE = 'amt_strike'
    AMT_STRIKE_BEFORE_ADJ = 'amt_strike_before_adj'
    AMT_CLOSE = 'amt_close'
    AMT_OPEN = 'amt_open'
    AMT_HIGH = 'amt_high'
    AMT_LOW = 'amt_low'
    AMT_ADJ_OPTION_PRICE = 'amt_adj_option_price'
    AMT_OPTION_PRICE = 'amt_option_price'
    AMT_UNDERLYING_CLOSE = 'amt_underlying_close'
    AMT_UNDERLYING_OPEN_PRICE = 'amt_underlying_open_price'
    AMT_SETTLEMENT = 'amt_settlement'
    AMT_LAST_SETTLEMENT = 'amt_last_settlement'
    AMT_LAST_CLOSE = 'amt_last_close'
    NBR_MULTIPLIER = 'nbr_multiplier'
    NBR_MULTIPLIER_AFTER_ADJ = 'nbr_multiplier_after_adj'
    AMT_HOLDING_VOLUME = 'amt_holding_volume'
    AMT_TRADING_VOLUME = 'amt_trading_volume'
    AMT_TRADING_VOLUME_CALL = 'amtl_trading_volume_call'
    AMT_TRADING_VOLUME_PUT = 'amt_trading_volume_put'
    AMT_TRADING_VALUE = 'amt_trading_value'
    AMT_MORNING_OPEN_15MIN = 'amt_morning_open_15min'
    AMT_MORNING_CLOSE_15MIN = 'amt_morning_close_15min'
    AMT_AFTERNOON_OPEN_15MIN = 'amt_afternoon_open_15min'
    AMT_AFTERNOON_CLOSE_15MIN = 'amt_afternoon_close_15min'
    AMT_MORNING_AVG = 'amt_morning_avg'
    AMT_AFTERNOON_AVG = 'amt_afternoon_avg'
    AMT_DAILY_AVG = 'amt_daily_avg'
    AMT_NEAREST_STRIKE = 'amt_nearest_strike'
    PCT_IMPLIED_VOL = 'pct_implied_vol'
    PCT_IV_OTM_BY_HTBR = 'pct_iv_by_htbr'
    PCT_IV_CALL_BY_HTBR = 'pct_iv_call_by_htbr'
    PCT_IV_PUT_BY_HTBR = 'pct_iv_put_by_htbr'
    PCT_IV_CALL = 'pct_iv_call'
    PCT_IV_PUT = 'pct_iv_put'
    AMT_DELTA = 'amt_delta'
    AMT_THETA = 'amt_theta'
    AMT_VEGA = 'amt_vega'
    AMT_RHO = 'amt_rho'
    AMT_CARRY = 'amt_carry'
    AMT_IV_ROLL_DOWN = 'amt_iv_roll_down'
    NBR_INVEST_DAYS = 'nbr_invest_days'
    RISK_FREE_RATE = 'risk_free_rate'
    AMT_APPLICABLE_STRIKE = 'amt_applicable_strike'
    AMT_APPLICABLE_MULTIPLIER = 'amt_applicable_multiplier'
    AMT_YIELD = 'amt_yield'
    AMT_HISTVOL = 'amt_hist_vol'
    AMT_PARKINSON_NUMBER = 'amt_parkinson_number'
    AMT_GARMAN_KLASS = 'amt_garman_klass'
    AMT_HEDHE_UNIT = 'amt_hedge_unit'
    AMT_CALL_QUOTE = 'amt_call_quote'
    ID_CALL = 'id_call'
    ID_PUT = 'id_put'
    AMT_PUT_QUOTE = 'amt_put_quote'
    AMT_TTM = 'amt_ttm'
    AMT_HTB_RATE = 'amt_HTB_rate'
    AMT_CLOSE_VOLUME_WEIGHTED = 'amt_close_volume_weighted'
    CD_CLOSE = 'cd_close'
    CD_CLOSE_VOLUME_WEIGHTED = 'cd_close_volume_weighted'
    NAME_CODE = 'name_code'
    STR_CALL = 'call'
    STR_PUT = 'put'
    STR_50ETF = '50etf'
    STR_INDEX_50ETF = 'index_50etf'
    STR_INDEX_50SH = 'index_50sh'
    STR_INDEX_300SH = 'index_300sh'
    STR_INDEX_300SH_TOTAL_RETURN = 'index_300sh_total_return'
    STR_M = 'm'
    STR_IH = 'ih'
    STR_IF = 'iF'
    STR_SR = 'sr'
    STR_ALL = 'all'
    STR_CU = 'cu'
    STR_CF = 'cf'
    STR_C = 'c'
    STR_RU = 'ru'
    NAN_VALUE = -999.0
    NAME_CODE_159 = ['sr', 'm', 'ru']
    MAIN_CONTRACT_159 = [1, 5, 9, '01', '05', '09']
    NAME_CODE_1to12 = ['cu']
    # Trade
    LONG = 1
    SHORT = -1
    UUID = 'uuid'
    DT_TRADE = 'dt_trade'
    TRADE_TYPE = 'trade_type'
    TRADE_PRICE = 'trade_price'
    TRANSACTION_COST = 'transaction_cost'
    TRADE_UNIT = 'trade_unit'  # 绝对值
    TIME_SIGNAL = 'time_signal'
    OPTION_PREMIIUM = 'option_premium'
    CASH = 'cash'
    TRADE_MARGIN_CAPITAL = 'trade_margin_capital'
    TRADE_MARKET_VALUE = 'trade_market_value'  # 头寸市值
    TRADE_BOOK_VALUE = 'trade_book_value'  # 头寸规模（含多空符号），例如，空一手豆粕（3000点，乘数10）得到头寸规模为-30000，而建仓时点头寸市值为0。
    ABS_TRADE_BOOK_VALUE = 'abs_trade_book_value'
    TRADE_LONG_SHORT = 'long_short'
    AVERAGE_POSITION_COST = 'average_position_cost'  # 历史多次交易同一品种的平均成本(总头寸规模绝对值/unit)
    TRADE_REALIZED_PNL = 'realized_pnl'
    LAST_PRICE = 'last_price'
    POSITION_CURRENT_VALUE = 'position_current_value'  # 用于计算杠杆率，保证金交易的current value为零
    PORTFOLIO_MARGIN_CAPITAL = 'portfolio_margin_capital'
    PORTFOLIO_MARGIN_TRADE_SCALE = 'portfolio_margin_trade_scale'
    PORTFOLIO_TOTAL_SCALE = 'portfolio_total_scale'
    PORTFOLIO_TRADES_VALUE = 'portfolio_trades_value'
    PORTFOLIO_VALUE = 'portfolio_value'
    PORTFOLIO_NPV = 'npv'
    PORTFOLIO_UNREALIZED_PNL = 'unrealized_pnl'
    PORTFOLIO_LEVERAGE = 'portfolio_leverage'
    PORTFOLIO_FUND_UTILIZATION = 'portfolio_fund_utilization'
    PORTFOLIO_SHORT_POSITION_SCALE = 'portfolio_short_position_scale'
    PORTFOLIO_LONG_POSITION_SCALE = 'portfolio_long_position_scale'
    MARGIN_UNREALIZED_PNL = 'margin_unrealized_pnl'
    NONMARGIN_UNREALIZED_PNL = 'nonmargin_unrealized_pnl'
    PORTFOLIO_DELTA = 'portfolio_delta'
    TURNOVER = 'turnover'
    DRAWDOWN = 'drawdown'
    DAILY_EXCECUTED_AMOUNT = 'daily_executed_amount'  # abs value
    BILLION = 1000000000.0
    MILLION = 1000000.0
    TRADE_BOOK_COLUMN_LIST = [DT_DATE, TRADE_LONG_SHORT, TRADE_UNIT,
                              LAST_PRICE, TRADE_MARGIN_CAPITAL,
                              TRADE_BOOK_VALUE, AVERAGE_POSITION_COST,
                              TRADE_REALIZED_PNL, NBR_MULTIPLIER,
                              TRANSACTION_COST
                              ]  # ID_INSTRUMENR是index
    ACCOUNT_COLUMNS = [DT_DATE, PORTFOLIO_NPV, PORTFOLIO_VALUE, CASH, PORTFOLIO_MARGIN_CAPITAL, PORTFOLIO_TRADES_VALUE,
                       PORTFOLIO_FUND_UTILIZATION, PORTFOLIO_DELTA, DAILY_EXCECUTED_AMOUNT
                       ]
    DICT_FUTURE_MARGIN_RATE = {  # 合约价值的百分比
        'm': 0.05,
        'sr': 0.05,
        'cu': 0.05,
        'if': 0.15,
        'ih': 0.15,
        'ic': 0.15,
        'index': 0.15
    }
    DICT_TRANSACTION_FEE = {  # 元/手
        'm': 3.0,
        'sr': 3.0,
        'cu': 3.0,
        'if': None,
        'ih': None,
        'ic': None,
        "index": 0
    }
    DICT_OPTION_TRANSACTION_FEE_RATE = {  # 百分比
        "50etf": 0.0,
        "m": 0.0,
        "sr": 0.0,
        "cu": 0.0,
    }
    DICT_OPTION_TRANSACTION_FEE = {  # 元/手
        "50etf": 5.0,
        "m": 5.0,
        "sr": 5.0,
        "cu": 5.0
    }
    DICT_TRANSACTION_FEE_RATE = {  # 百分比
        'm': None,
        'sr': None,
        'cu': None,
        'if': 6.9 / 10000.0,
        'ih': 6.9 / 10000.0,
        'ic': 6.9 / 10000.0,
        "index": None
    }
    DICT_CONTRACT_MULTIPLIER = {  # 合约乘数
        'm': 10,
        'sr': 10,
        'cu': 5,
        'if': 300,
        'ih': 300,
        'ic': 200,
        'index': 1
    }
    DICT_OPTION_CONTRACT_MULTIPLIER = {  # 合约乘数
        'm': 10,
        'sr': 10,
        STR_50ETF: 10000
    }
    DICT_FUTURE_CORE_CONTRACT = {
        'm': [1, 5, 9],
        'sr': [1, 5, 6],
        STR_50ETF: STR_ALL}

    DICT_TICK_SIZE = {
        "50etf": 0.0001,
        "m": 1,
        "sr": 0.5,
        'if': 0.2,
        'ih': 0.2,
        'ic': 0.2,
        'index': 0
    }


class HistoricalVolatility:

    @staticmethod
    def hist_vol_daily(closes, n=20):
        series = np.log(closes).diff()
        res_series = series.rolling(window=n).std()
        return res_series

    @staticmethod
    def hist_vol(closes, n=20):
        series = np.log(closes).diff()
        res_series = series.rolling(window=n).std() * math.sqrt(252)
        return res_series

    @staticmethod
    def parkinson_number(df, n=20):
        squred_log_h_l = df.apply(HistoricalVolatility.fun_squred_log_high_low, axis=1)
        sum_squred_log_h_l = squred_log_h_l.rolling(window=n).sum()
        res_series = sum_squred_log_h_l.apply(
            lambda x: math.sqrt(252 * x / (n * 4 * math.log(2))))
        return res_series

    @staticmethod
    def garman_klass(df, n=20):
        tmp = df.apply(HistoricalVolatility.fun_garman_klass, axis=1)
        sum_tmp = tmp.rolling(window=n).sum()
        res_resies = sum_tmp.apply(lambda x: math.sqrt(x * 252 / n))
        return res_resies

    @staticmethod
    def fun_squred_log_high_low(df: pd.Series) -> float:
        return (math.log(df[Util.AMT_HIGH] / df[Util.AMT_LOW])) ** 2

    @staticmethod
    def fun_squred_log_close_open(df: pd.Series) -> float:
        return (math.log(df[Util.AMT_CLOSE] / df[Util.AMT_OPEN])) ** 2

    @staticmethod
    def fun_garman_klass(df: pd.Series) -> float:
        return 0.5 * HistoricalVolatility.fun_squred_log_high_low(df) - (
                    2 * math.log(2) - 1) * HistoricalVolatility.fun_squred_log_close_open(df)
