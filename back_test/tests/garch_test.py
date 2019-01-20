import datetime
from arch import arch_model
import numpy as np
import pandas as pd
import sys
import pandas_datareader.data as web


start = datetime.datetime(2000, 1, 1)
end = datetime.datetime(2017, 1, 1)
data = web.get_data_famafrench('F-F_Research_Data_Factors_daily', start=start, end=end)
mkt_returns = data[0]['Mkt-RF'] + data[0]['RF']
returns = mkt_returns
variances = (returns.rolling(window=10).std()) ** 2
am = arch_model(returns, vol='Garch', p=1, o=0, q=1, dist='Normal')
res = am.fit(update_freq=5)

forecasts = res.forecast()
print(forecasts.mean.iloc[-3:])
print(forecasts.residual_variance.iloc[-3:])
print(forecasts.variance.iloc[-3:])

forecasts = res.forecast(horizon=5)
print(forecasts.residual_variance.iloc[-3:])

# Fixed Window Forecasting :
# Note last_obs follow Python sequence rules so that
# the actual date in last_obs is not in the sample.
res = am.fit(last_obs='2011-1-1', update_freq=5)
forecasts = res.forecast(horizon=5)
print(forecasts.variance.dropna().head())

index = returns.index
start_loc = 0
end_loc = np.where(index >= '2010-1-1')[0].min()
forecasts = {}
for i in range(20):
    sys.stdout.write('.')
    sys.stdout.flush()
    res = am.fit(first_obs=i, last_obs=i + end_loc, disp='off')
    temp = res.forecast(horizon=3).variance
    fcast = temp.iloc[i + end_loc - 1]
    fcast['hist_variance'] = variances.iloc[i + end_loc]
    forecasts[fcast.name] = fcast

print()
print(pd.DataFrame(forecasts).T)

# Recursive Forecast Generation
index = returns.index
start_loc = 0
end_loc = np.where(index >= '2010-1-1')[0].min()
forecasts = {}
for i in range(20):
    sys.stdout.write('.')
    sys.stdout.flush()
    res = am.fit(first_obs=i, last_obs=i + end_loc, disp='off')
    temp = res.forecast(horizon=3).variance
    fcast = temp.iloc[i + end_loc - 1]
    fcast['hist_variance'] = variances.iloc[i + end_loc]
    forecasts[fcast.name] = fcast

print()
print(pd.DataFrame(forecasts).T)
