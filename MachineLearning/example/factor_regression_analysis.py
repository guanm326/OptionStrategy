# encoding: utf-8
from back_test.model.constant import Regression
import pandas as pd

df_data = pd.read_csv('data.csv')
print(df_data)

df_data['y'] = df_data['vol'].shift(-1)
df_data = df_data.dropna()
print("="*50)
print("### alpha_my0 ###")
print("-"*50)
reg = Regression.linear_regression(x=df_data['alpha_my0'],y=df_data['y'])
print(pd.DataFrame({'params':reg.params,'pvalues':reg.pvalues}))
print('R2  ',reg.rsquared)

print("="*50)
print("### alpha_my1 ###")
print("-"*50)
reg = Regression.linear_regression(x=df_data['alpha_my1'],y=df_data['y'])
print(pd.DataFrame({'params':reg.params,'pvalues':reg.pvalues}))
print('R2',reg.rsquared)

print("="*50)
print("### alpha_my2 ###")
print("-"*50)
reg = Regression.linear_regression(x=df_data['alpha_my2'],y=df_data['y'])
print(pd.DataFrame({'params':reg.params,'pvalues':reg.pvalues}))

print('R2',reg.rsquared)