import datetime
from data_access.get_data import get_index_mktdata, get_iv_by_moneyness
from back_test.model.constant import HistoricalVolatility, Util
from arch import arch_model
import numpy as np
import pandas as pd
import sys
import math
from statsmodels.graphics.tsaplots import plot_acf
import matplotlib.pyplot as plt
from WindPy import w

class Arch(object):

    def __init__(self, df_data, df_iv=None):
        df_data.loc[:, 'r'] = HistoricalVolatility.log_yield(df_data[Util.AMT_CLOSE])
        df_data.loc[:, 'hv_20'] = HistoricalVolatility.hist_vol(df_data[Util.AMT_CLOSE], n=20)
        df_data = df_data.dropna()
        if df_iv is not None:
            df_data = df_data.join(df_iv[[Util.DT_DATE, Util.PCT_IMPLIED_VOL]].set_index(Util.DT_DATE),
                                   on=Util.DT_DATE, how='left')
        else:
            df_data.loc[:, Util.PCT_IMPLIED_VOL] = None
        self.df_data = df_data.set_index(Util.DT_DATE)
        self.returns = self.df_data['r']*100

    def autocorrelation(self):
        plot_acf(self.returns)
        plt.show()

    def arch(self):
        model = arch_model(self.returns, mean='Zero', vol='ARCH', p=5)
        model_fit = model.fit(disp='off')
        print(model_fit.summary())
        forecasts = model_fit.forecast(horizon=5)
        print(forecasts.variance.iloc[-3:] ** 0.5 * math.sqrt(252) / 100)
        print(self.df_data.iloc[-3:])

    def garch(self):
        am = arch_model(self.returns, vol='garch', p=1, q=1, dist='t')
        res = am.fit(disp='off')
        print(res.summary())
        forecasts = res.forecast(horizon=5)
        print(forecasts.variance.iloc[-3:] ** 0.5 * math.sqrt(252)/100)
        print(self.df_data.iloc[-3:])

    def recursive_forecast_generation(self):
        am = arch_model(self.returns, vol='Garch', p=1, q=1, dist='t')
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


df_c1 = get_index_mktdata(datetime.date(2018, 1, 1), datetime.date(2018, 12, 31), Util.STR_INDEX_300SH)[[Util.DT_DATE, Util.AMT_CLOSE]]
arch = Arch(df_c1)

arch.recursive_forecast_generation()
