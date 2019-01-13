import math
import pandas as pd
import numpy as np
from back_test.model.constant import Util


class HistoricalVolatilityModels:

    @staticmethod
    def hist_vol(closes,n=20):
        series = np.log(closes).diff()
        res_series = series.rolling(window=n).std() * math.sqrt(252)
        return res_series

    @staticmethod
    def parkinson_number(df,n=20):
        # df_vol = df[[Util.DT_DATE]]
        squred_log_h_l = df.apply(HistoricalVolatilityModels.fun_squred_log_high_low, axis=1)
        sum_squred_log_h_l = squred_log_h_l.rolling(window=n).sum()
        res_series = sum_squred_log_h_l.apply(
            lambda x: math.sqrt(252 * x / (n * 4 * math.log(2))))
        # df_vol[Util.AMT_PARKINSON_NUMBER+'_'+str(n)] = sum_squred_log_h_l.apply(
        #     lambda x: math.sqrt(252 * x / (n * 4 * math.log(2))))
        # df_vol = df_vol.dropna().set_index(Util.DT_DATE)
        return res_series

    @staticmethod
    def garman_klass(df, n=20):
        # df_vol = df[[Util.DT_DATE]]
        tmp = df.apply(HistoricalVolatilityModels.fun_garman_klass, axis=1)
        sum_tmp = tmp.rolling(window=n).sum()
        res_resies = sum_tmp.apply(lambda x: math.sqrt(x * 252 / n))
        # df_vol[Util.AMT_GARMAN_KLASS+'_'+str(n)] = sum_tmp.apply(lambda x:math.sqrt(x*252/n))
        # df_vol = df_vol.dropna().set_index(Util.DT_DATE)
        return res_resies

    @staticmethod
    def fun_squred_log_high_low(df: pd.Series) -> float:
        return (math.log(df[Util.AMT_HIGH] / df[Util.AMT_LOW])) ** 2

    @staticmethod
    def fun_squred_log_close_open(df: pd.Series) -> float:
        return (math.log(df[Util.AMT_CLOSE] / df[Util.AMT_OPEN])) ** 2

    @staticmethod
    def fun_garman_klass(df: pd.Series) -> float:
        return 0.5 * HistoricalVolatilityModels.fun_squred_log_high_low(df) - (2 * math.log(2) - 1) * HistoricalVolatilityModels.fun_squred_log_close_open(df)



