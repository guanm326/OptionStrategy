from data_access.get_data import get_50option_mktdata as option_data
from back_test.model.base_option_set import BaseOptionSet
from back_test.model.constant import Util, OptionUtil
import datetime
import math
import pandas as pd
import Utilities.admin_write_util as admin


class Indexing():
    def __init__(self, start_date, end_date):
        df_metrics = option_data(start_date, end_date)
        self.optionset = BaseOptionSet(df_metrics, rf=0.03)
        self.optionset.init()

    def fun_otm_quote(self, df):
        if df[Util.AMT_APPLICABLE_STRIKE] > df['mid_k']:
            quote = df['amt_call_quote']
        elif df[Util.AMT_APPLICABLE_STRIKE] < df['mid_k']:
            quote = df['amt_put_quote']
        else:
            quote = (df['amt_call_quote'] + df['amt_put_quote']) / 2.0
        return quote

    def fun_for_p1(self, df):
        DK = df['amt_delta_k']
        Q = df['amt_otm_quote']
        K = df[Util.AMT_APPLICABLE_STRIKE]
        res = Q * DK / K ** 2
        return Q * DK / K ** 2

    def fun_for_p2(self, df):
        DK = df['amt_delta_k']
        Q = df['amt_otm_quote']
        K = df[Util.AMT_APPLICABLE_STRIKE]
        F = df['F']
        return 2 * (1 - math.log(K / F, math.e)) * Q * DK / K ** 2

    def fun_for_p3(self, df):
        DK = df['amt_delta_k']
        Q = df['amt_otm_quote']
        K = df[Util.AMT_APPLICABLE_STRIKE]
        F = df['F']
        return 3 * (2 * math.log(K / F, math.e) - math.log(K / F, math.e) ** 2) * Q * DK / K ** 2

    def fun_for_sigma(self, df):
        DK = df['amt_delta_k']
        Q = df['amt_otm_quote']
        K = df[Util.AMT_APPLICABLE_STRIKE]
        return Q * DK / K ** 2

    def get_e1(self, F, K):
        return -(1 + math.log(F / K, math.e) - F / K)

    def get_e2(self, F, K):
        return 2 * math.log(K / F, math.e) * (F / K - 1) + 0.5 * math.log(K / F, math.e) ** 2

    def get_e3(self, F, K):
        return 3 * (math.log(K / F, math.e) ** 2) * ((1.0 / 3.0) * math.log(K / F, math.e) + F / K - 1)

    def get_S(self, p1, p2, p3):
        res = (p3 - 3 * p1 * p2 + 2 * p1 ** 3) / (p2 - p1 ** 2) ** 1.5
        return res

    def get_T_quotes(self, df_mdt, eval_date):
        df_call = df_mdt[df_mdt[Util.CD_OPTION_TYPE] == Util.STR_CALL].rename(
            columns={Util.AMT_CLOSE: 'amt_call_quote'})
        df_put = df_mdt[df_mdt[Util.CD_OPTION_TYPE] == Util.STR_PUT].rename(
            columns={Util.AMT_CLOSE: 'amt_put_quote'})
        df_call = df_call.drop_duplicates(Util.AMT_APPLICABLE_STRIKE).reset_index(drop=True)
        df_put = df_put.drop_duplicates(Util.AMT_APPLICABLE_STRIKE).reset_index(drop=True)

        df = pd.merge(df_call[['amt_call_quote', Util.AMT_APPLICABLE_STRIKE, Util.AMT_STRIKE]],
                      df_put[['amt_put_quote', Util.AMT_APPLICABLE_STRIKE]],
                      how='inner', on=Util.AMT_APPLICABLE_STRIKE)
        # df = pd.concat([df_call[['amt_call_quote']], df_put[['amt_put_quote']]], axis=1, join='inner', verify_integrity=True)
        df[Util.AMT_UNDERLYING_CLOSE] = df_put[Util.AMT_UNDERLYING_CLOSE].values[0]
        df['amt_cp_diff'] = abs(df['amt_call_quote'] - df['amt_put_quote'])
        maturitydt = df_put[Util.DT_MATURITY].values[0]
        df[Util.DT_MATURITY] = maturitydt
        ttm = ((maturitydt - eval_date).total_seconds() / 60.0) / (365.0 * 1440)
        df['amt_ttm'] = ttm
        df['amt_fv'] = math.exp(self.optionset.rf * (ttm))
        df = df.sort_values(by=Util.AMT_APPLICABLE_STRIKE).reset_index(drop=True)
        dk = df[Util.AMT_APPLICABLE_STRIKE].diff(periods = 2).dropna() / 2.0
        dk.loc[1] = df.loc[1,Util.AMT_APPLICABLE_STRIKE] - df.loc[0,Util.AMT_APPLICABLE_STRIKE]
        dk.loc[len(df)] = df.loc[len(df)-1,Util.AMT_APPLICABLE_STRIKE] - df.loc[len(df)-2,Util.AMT_APPLICABLE_STRIKE]
        dk = dk.sort_index()
        dk = dk.reset_index(drop=True)
        df['amt_delta_k'] = dk
        return df

    def forward_cboe(self, t_quotes, eval_date):
        # ATM strike k0 -- First strike below the forward index level, F
        # Forward price F -- F, by identifying the strike price at which the absolute difference
        # between the call and put prices is smallest.
        df = t_quotes.set_index(Util.AMT_APPLICABLE_STRIKE)
        mid_k = df.sort_values(by='amt_cp_diff', ascending=True).index[0]
        p_call = df.loc[mid_k, 'amt_call_quote']
        p_put = df.loc[mid_k, 'amt_put_quote']
        F = df.loc[mid_k, 'amt_fv'] * (p_call - p_put) + mid_k
        df['k-f'] = df.index - F
        if len(df[df['k-f'] < 0]) > 0:
            K0 = df[df['k-f'] < 0].sort_values(by='amt_cp_diff', ascending=True).index[0]
        else:
            K0 = df.sort_values(by='amt_cp_diff', ascending=True).index[0]
        return mid_k, K0, F

    """ K0 is the 1st strike below F0 """
    def for_calculation(self, df, eval_date):
        mid_k, k0, F = self.forward_cboe(df, eval_date)
        ttm = df.loc[0, 'amt_ttm']
        S = df.loc[0, 'amt_underlying_close']
        implied_r = math.log(F/S,math.e)/ttm
        self.implied_rf = implied_r
        df['k0'] = k0
        df['mid_k'] = mid_k
        df['F'] = F
        df['amt_otm_quote'] = df.apply(self.fun_otm_quote, axis=1)
        return df

    def calculate_S_for_skew(self, df):
        k0 = df.loc[0, 'k0']
        F = df.loc[0, 'F']
        e1 = self.get_e1(F, k0)
        e2 = self.get_e2(F, k0)
        e3 = self.get_e3(F, k0)
        df['for_p1'] = df.apply(self.fun_for_p1, axis=1)
        df['for_p2'] = df.apply(self.fun_for_p2, axis=1)
        df['for_p3'] = df.apply(self.fun_for_p3, axis=1)
        fv = df.loc[0, 'amt_fv']
        p1 = -fv * df['for_p1'].sum() + e1
        p2 = fv * df['for_p2'].sum() + e2
        p3 = fv * df['for_p3'].sum() + e3
        S = self.get_S(p1, p2, p3)
        SKEW = 100-10*S
        # S_r = self.get_S(-0.00173,0.003606,-0.00049)
        # SKEW_r = 100-10*S_r
        return S

    def calculate_sigma_for_vix(self, df):
        df['for_sigma'] = df.apply(self.fun_for_sigma, axis=1)
        k0 = df.loc[0, 'k0']
        F = df.loc[0, 'F']
        T = df.loc[0, 'amt_ttm']
        fv = df.loc[0, 'amt_fv']
        v1 = (1.0 / T) * (F / k0 - 1) ** 2
        # v1 = (F / K - 1) ** 2
        sum = df['for_sigma'].sum()
        sigma = (2.0 / T) * fv * sum - v1
        # sigma = 2.0 * fv * sum - v1
        return sigma

    def calculate(self, eval_date):
        df_daily_state = self.optionset.get_current_state()
        mdt = self.optionset.get_maturities_list()[0]
        if (mdt - self.optionset.eval_date).days <= 5:
            mdt1 = self.optionset.get_maturities_list()[1]
            mdt2 = self.optionset.get_maturities_list()[2]
        else:
            mdt1 = self.optionset.get_maturities_list()[0]
            mdt2 = self.optionset.get_maturities_list()[1]
        df_mdt1 = OptionUtil.get_df_by_mdt(df_daily_state, mdt1)
        df_mdt2 = OptionUtil.get_df_by_mdt(df_daily_state, mdt2)
        t_quotes1 = self.get_T_quotes(df_mdt1, eval_date)
        t_quotes2 = self.get_T_quotes(df_mdt2, eval_date)
        # t_quotes1.to_csv('t_quotes1.csv')
        # t_quotes2.to_csv('t_quotes2.csv')
        calculate1 = self.for_calculation(t_quotes1, eval_date)
        calculate2 = self.for_calculation(t_quotes2, eval_date)
        S1 = self.calculate_S_for_skew(calculate1)
        S2 = self.calculate_S_for_skew(calculate2)

        sigma1 = self.calculate_sigma_for_vix(calculate1)
        sigma2 = self.calculate_sigma_for_vix(calculate2)
        T1 = calculate1.loc[0, 'amt_ttm']
        T2 = calculate2.loc[0, 'amt_ttm']
        NT1 = (mdt1 - eval_date).total_seconds() / 60.0
        NT2 = (mdt2 - eval_date).total_seconds() / 60.0
        N30 = 30 * 1440.0
        N365 = 365 * 1440.0
        w = (NT2 - N30) / (NT2 - NT1)
        skew = 100 - 10 * (w * S1 + (1 - w) * S2)
        vix = 100 * math.sqrt((T1 * sigma1 * w + T2 * sigma2 * (1 - w)) * N365 / N30)
        return vix, skew

    def get_atm_options(self, maturity):
        list_atm_call, list_atm_put = self.optionset.get_options_list_by_moneyness_mthd1(moneyness_rank=0, maturity=maturity)
        atm_call = self.optionset.select_higher_volume(list_atm_call)
        atm_put = self.optionset.select_higher_volume(list_atm_put)
        return atm_call, atm_put

    def get_atm_iv_average(self, maturity):
        atm_call, atm_put = self.get_atm_options(maturity)
        iv_call = atm_call.get_implied_vol()
        iv_put = atm_put.get_implied_vol()
        iv_avg = (iv_call + iv_put) / 2
        return iv_avg

    def run(self):
        self.df_res = pd.DataFrame()
        print('=' * 120)
        print("%10s %20s %20s %20s %20s %20s" % ('eval_date', 'vix', 'skew', 'iv_htr', 'iv_avg', 'htbr'))
        print('-' * 120)
        table_iv = admin.table_implied_volatilities()
        while self.optionset.current_index < self.optionset.nbr_index:
            eval_date = self.optionset.eval_date
            try:
                maturity = self.optionset.select_maturity_date(nbr_maturity, min_holding=min_holding)
                iv_htr = self.optionset.get_atm_iv_by_htbr(maturity)
                iv_avg = self.get_atm_iv_average(maturity)
                htbr = self.optionset.get_htb_rate(maturity)
                vix, skew = self.calculate(eval_date)
                self.df_res.loc[eval_date, 'skew'] = skew
                self.df_res.loc[eval_date, 'vix'] = vix
                self.df_res.loc[eval_date, '50ETF'] = self.optionset.get_underlying_close()
                self.df_res.loc[eval_date, 'htb_rate'] = htbr
                self.df_res.loc[eval_date, 'iv_atm_htr'] = iv_htr
                self.df_res.loc[eval_date, 'iv_atm_avg'] = iv_avg
                print("%10s %20s %20s %20s %20s %20s" % (eval_date,vix, skew, iv_htr,iv_avg,htbr))
                res = {
                    'dt_date': self.optionset.eval_date,
                    'name_code': Util.STR_50ETF,
                    'id_underlying': 'index_50etf',
                    'cd_option_type': 'ivix',
                    'cd_mdt_selection': 'hp_8_1st',
                    'cd_atm_criterion': 'nearest_strike',
                    'nbr_moneyness': 0,
                    'cd_source': 'quantlib',
                    'id_instrument': None,
                    'dt_maturity': maturity,
                    'pct_implied_vol': vix/100.0,
                    'amt_close': None,
                    'amt_strike': None,
                    'amt_applicable_strike': None,
                    'amt_underlying_close': None
                }
                try:
                    admin.conn_metrics().execute(table_iv.insert(), res)
                    print('inserted into data base succefully ', res['dt_date'])
                except Exception as e:
                    print(e)
                    pass
            except:
                pass
            if not self.optionset.has_next():break
            self.optionset.next()




start_date = datetime.date(2015, 6, 1)
# start_date = datetime.date.today() - datetime.timedelta(days=10)
end_date = datetime.date.today()
nbr_maturity = 0
min_holding = 8
skew_indexing = Indexing(start_date, end_date)
skew_indexing.run()
res = skew_indexing.df_res.sort_index(ascending=False)
res.to_csv('../../data/indexes.csv')


