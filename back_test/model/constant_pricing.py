import pandas as pd
from typing import List, Union
import math
import datetime
import QuantLib as ql
from back_test.model.constant import Util,OptionType

class OptionFilter:
    dict_maturities = {'m_1707': datetime.date(2017, 6, 7),
                       'm_1708': datetime.date(2017, 7, 7),
                       'm_1709': datetime.date(2017, 8, 7),
                       'm_1711': datetime.date(2017, 10, 13),
                       'm_1712': datetime.date(2017, 11, 7),
                       'sr_1707': datetime.date(2017, 5, 23),
                       'sr_1709': datetime.date(2017, 7, 25),
                       'sr_1711': datetime.date(2017, 9, 25),
                       'sr_1801': datetime.date(2017, 11, 24),
                       'cu_1901': datetime.date(2018, 12, 25),
                       'cu_1902': datetime.date(2019, 1, 25),
                       'cu_1903': datetime.date(2019, 2, 22),
                       'cu_1904': datetime.date(2019, 3, 25),
                       'cu_1905': datetime.date(2019, 4, 24),
                       'cu_1906': datetime.date(2019, 5, 27),
                       'cu_1907': datetime.date(2019, 6, 24),
                       'cu_1908': datetime.date(2019, 7, 25),
                       'cu_1909': datetime.date(2019, 8, 26),
                       'cu_1910': datetime.date(2019, 9, 24),
                       'cu_1911': datetime.date(2019, 10, 25),
                       'cu_1912': datetime.date(2019, 11, 25),
                       'cu_2001': datetime.date(2019, 12, 25),
                       }

    @staticmethod
    def fun_option_type_split(df: pd.Series) -> Union[str, None]:
        id_instrument = df[Util.ID_INSTRUMENT]
        type_str = id_instrument.split('_')[2]
        if type_str == 'c':
            option_type = Util.STR_CALL
        elif type_str == 'p':
            option_type = Util.STR_PUT
        else:
            return
        return option_type

    @staticmethod
    def fun_option_price(df: pd.Series) -> float:
        if df[Util.AMT_CLOSE] != Util.NAN_VALUE:
            option_price = df[Util.AMT_CLOSE]
        elif df[Util.AMT_SETTLEMENT] != Util.NAN_VALUE:
            option_price = df[Util.NAN_VALUE]
        else:
            print('amt_close and amt_settlement are null!')
            print(df)
            option_price = None
        return option_price

    @staticmethod
    def nearest_strike_level(s: pd.Series) -> float:
        strike = s[Util.AMT_STRIKE]
        if strike <= 3:
            return round(round(strike / 0.05) * 0.05, 2)
        else:
            return round(round(strike / 0.1) * 0.1, 2)

    @staticmethod
    def fun_option_maturity(df):
        if df[Util.DT_MATURITY] is None or pd.isnull(df[Util.DT_MATURITY]):
            return OptionFilter.dict_maturities[df[Util.ID_UNDERLYING]]
        else:
            return df[Util.DT_MATURITY]

    @staticmethod
    def generate_commodity_option_maturities():
        maturity_date = 0
        dict_option_maturity = {}
        id_list = ['m_1707', 'm_1708', 'm_1709', 'm_1711', 'm_1712']
        calendar = ql.China()
        for contractId in id_list:
            year = '201' + contractId[3]
            month = contractId[-2:]
            date = ql.Date(1, int(month), int(year))
            maturity_date = calendar.advance(calendar.advance(date, ql.Period(-1, ql.Months)), ql.Period(4, ql.Days))
            dt_maturity = QuantlibUtil.to_dt_date(maturity_date)
            dict_option_maturity.update({contractId: dt_maturity})
        id_list_sr = ['sr_1707', 'sr_1709', 'sr_1711', 'sr_1801']
        for contractId in id_list_sr:
            year = '201' + contractId[4]
            month = contractId[-2:]
            date = ql.Date(1, int(month), int(year))
            maturity_date = calendar.advance(calendar.advance(date, ql.Period(-1, ql.Months)), ql.Period(-5, ql.Days))
            dt_maturity = QuantlibUtil.to_dt_date(maturity_date)
            dict_option_maturity.update({contractId: dt_maturity})
        print(dict_option_maturity)
        return maturity_date

class PricingUtil:
    @staticmethod
    def payoff(spot: float, strike: float, option_type: OptionType):
        return abs(max(option_type.value * (spot - strike), 0.0))

    @staticmethod
    def get_ttm(dt_eval, dt_maturity):
        N = (dt_maturity - dt_eval).total_seconds() / 60.0
        N365 = 365 * 1440.0
        ttm = N / N365
        return ttm


    @staticmethod
    def get_std(dt_eval, dt_maturity, annualized_vol):
        # try:
        stdDev = annualized_vol * math.sqrt(PricingUtil.get_ttm(dt_eval, dt_maturity))
        # except:
        #     print('')
        #     pass
        return stdDev

    @staticmethod
    def get_discount(dt_eval, dt_maturity, rf):
        discount = math.exp(-rf * PricingUtil.get_ttm(dt_eval, dt_maturity))
        return discount

    @staticmethod
    def get_maturity_metrics(self, dt_date, spot, option):
        strike = option.strike
        if option.option_type == OptionType.PUT:
            if strike > spot:  # ITM
                delta = -1.0
            elif strike < spot:  # OTM
                delta = 0.0
            else:
                delta = 0.5
            option_price = max(strike - spot, 0)
        else:
            if strike < spot:  # ITM
                delta = 1.0
            elif strike > spot:  # OTM
                delta = 0.0
            else:
                delta = 0.5
            option_price = max(spot - strike, 0)
        delta = delta
        option_price = option_price
        return delta, option_price

    @staticmethod
    def get_mdate_by_contractid(commodityType, contractId, calendar):
        maturity_date = 0
        if commodityType == 'm':
            year = '20' + contractId[0: 2]
            month = contractId[-2:]
            date = ql.Date(1, int(month), int(year))
            maturity_date = calendar.advance(calendar.advance(date, ql.Period(-1, ql.Months)), ql.Period(4, ql.Days))
        elif commodityType == 'sr':
            year = '201' + contractId[2]
            month = contractId[-2:]
            date = ql.Date(1, int(month), int(year))
            maturity_date = calendar.advance(calendar.advance(date, ql.Period(-1, ql.Months)), ql.Period(-5, ql.Days))
        return maturity_date

class QuantlibUtil:
    @staticmethod
    def to_dt_dates(ql_dates):
        datetime_dates = []
        for d in ql_dates:
            dt = datetime.date(d.year(), d.month(), d.dayOfMonth())
            datetime_dates.append(dt)
        return datetime_dates

    @staticmethod
    def to_ql_dates(datetime_dates):
        ql_dates = []
        for d in datetime_dates:
            dt = ql.Date(d.day, d.month, d.year)
            ql_dates.append(dt)
        return ql_dates

    @staticmethod
    def to_ql_date(datetime_date):
        dt = ql.Date(datetime_date.day, datetime_date.month, datetime_date.year)
        return dt

    @staticmethod
    def to_dt_date(ql_date):
        dt = datetime.date(ql_date.year(), ql_date.month(), ql_date.dayOfMonth())
        return dt

    # @staticmethod
    # def get_curve_treasury_bond(evalDate, daycounter):
    #     datestr = str(evalDate.year()) + "-" + str(evalDate.month()) + "-" + str(evalDate.dayOfMonth())
    #     try:
    #         curvedata = pd.read_json(os.path.abspath('..') + '\marketdata\curvedata_tb_' + datestr + '.json')
    #         rates = curvedata.values[0]
    #         calendar = ql.China()
    #         dates = [evalDate,
    #                  calendar.advance(evalDate, ql.Period(1, ql.Months)),
    #                  calendar.advance(evalDate, ql.Period(3, ql.Months)),
    #                  calendar.advance(evalDate, ql.Period(6, ql.Months)),
    #                  calendar.advance(evalDate, ql.Period(9, ql.Months)),
    #                  calendar.advance(evalDate, ql.Period(1, ql.Years))]
    #         krates = np.divide(rates, 100)
    #         curve = ql.ForwardCurve(dates, krates, daycounter)
    #     except Exception as e:
    #         print(e)
    #         print('Error def -- get_curve_treasury_bond in \'svi_read_data\' on date : ', evalDate)
    #         return
    #     return curve

    #
    # @staticmethod
    # def get_rf_tbcurve(evalDate, daycounter, maturitydate):
    #     curve = get_curve_treasury_bond(evalDate, daycounter)
    #     maxdate = curve.maxDate()
    #     # print(maxdate,maturitydate)
    #     if maturitydate > maxdate:
    #         rf = curve.zeroRate(maxdate, daycounter, ql.Continuous).rate()
    #     else:
    #         rf = curve.zeroRate(maturitydate, daycounter, ql.Continuous).rate()
    #     return rf

    @staticmethod
    def get_yield_ts(evalDate, curve, mdate, daycounter):
        maxdate = curve.maxDate()
        if mdate > maxdate:
            rf = curve.zeroRate(maxdate, daycounter, ql.Continuous).rate()
        else:
            rf = curve.zeroRate(mdate, daycounter, ql.Continuous).rate()
        yield_ts = ql.YieldTermStructureHandle(ql.FlatForward(evalDate, rf, daycounter))
        return yield_ts

    @staticmethod
    def get_dividend_ts(evalDate, daycounter):
        dividend_ts = ql.YieldTermStructureHandle(ql.FlatForward(evalDate, 0.0, daycounter))
        return dividend_ts

    @staticmethod
    def get_business_between(dt_start,dt_end):
        calendar = ql.China()
        t = calendar.businessDaysBetween(QuantlibUtil.to_ql_date(dt_start),QuantlibUtil.to_ql_date(dt_end))
        return t








