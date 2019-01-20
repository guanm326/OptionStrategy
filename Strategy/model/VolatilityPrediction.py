import datetime
from data_access.get_data import get_index_mktdata, get_iv_by_moneyness
from back_test.model.constant import HistoricalVolatility, Util
from arch import arch_model
import numpy as np
import pandas as pd
import sys
import math


class Garch(object):

    def __init__(self, df_data, df_iv=None):
        df_data.loc[:, 'r'] = HistoricalVolatility.arithmetic_yield(df_data[Util.AMT_CLOSE])
        df_data.loc[:, 'hv_20'] = HistoricalVolatility.hist_vol(df_data[Util.AMT_CLOSE], n=20)
        df_data = df_data.dropna()
        if df_iv is not None:
            df_data = df_data.join(df_iv[[Util.DT_DATE, Util.PCT_IMPLIED_VOL]].set_index(Util.DT_DATE),
                                   on=Util.DT_DATE, how='left')
        else:
            df_data.loc[:, Util.PCT_IMPLIED_VOL] = None
        self.df_data = df_data.set_index(Util.DT_DATE)
        self.returns = self.df_data['r']*100

    def basic_forcasting(self):
        am = arch_model(self.returns, vol='Garch', p=1, o=0, q=1, dist='Normal')
        res = am.fit(update_freq=10)
        # f = np.sqrt(res.params['omega'] + res.params['alpha[1]'] * res.resid**2 + res.conditional_volatility**2 * res.params['beta[1]'])
        print(res.summary())
        forecasts = res.forecast(horizon=5)
        print(forecasts.variance.iloc[-3:] ** 0.5 * math.sqrt(252)/100)

    def recursive_forecast_generation(self):
        am = arch_model(self.returns, vol='Garch', p=1, o=0, q=1, dist='Normal')
        end_loc = 100  # 基于一百个数据预测
        max_loc = len(self.returns.index) - 1
        forecasts = {}
        for i in range(max_loc - end_loc):
            # sys.stdout.write('.')
            sys.stdout.flush()
            res = am.fit(last_obs=i + end_loc, disp='off')
            temp = res.forecast(horizon=3).variance ** 0.5 * math.sqrt(252)/100
            fcast = temp.iloc[i + end_loc - 1]
            fcast['hv_20'] = self.df_data.iloc[i + end_loc]['hv_20']
            fcast['iv'] = self.df_data.iloc[i + end_loc][Util.PCT_IMPLIED_VOL]
            forecasts[fcast.name] = fcast
        print()
        print(pd.DataFrame(forecasts).T)


df_c1 = get_index_mktdata(datetime.date(2018, 1, 1), datetime.date(2018, 12, 31), Util.STR_INDEX_50ETF)
df_iv = get_iv_by_moneyness(datetime.date(2018, 1, 1), datetime.date(2018, 12, 31),Util.STR_50ETF,nbr_moneyness=0)
garch = Garch(df_c1[[Util.DT_DATE, Util.AMT_CLOSE]],df_iv[[Util.DT_DATE,Util.PCT_IMPLIED_VOL]])
garch.basic_forcasting()
# garch.recursive_forecast_generation()
