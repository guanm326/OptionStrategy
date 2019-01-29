import math
import datetime
from scipy.stats import norm
from back_test.model.constant import OptionType,PricingUtil
from PricingLibrary.BlackCalculator import BlackCalculator
###########Sythetic Option 2019-1-7#############
# dt_eval = datetime.date.today()
# mdt = datetime.date.today() + datetime.timedelta(days=50)
# k = 4376.44
# vol = 0.2536
# spot = 4288.3234
# call = BlackCalculator(datetime.date.today(),mdt,k,OptionType.CALL,spot,vol)
# print(call.Delta())
# print(call.Gamma())
# gamma = call.Gamma()
# rho = 0.01
# tao = PricingUtil.get_ttm(dt_eval, mdt)
# H = (1.5 * math.exp(-0.03*tao) * (1.0/1000.0) * spot * (gamma ** 2) / rho) ** (1 / 3)
# print(H)

#########Sythetic Option 2019-1-9#############
dt_eval = datetime.date.today()
mdt = datetime.date.today() + datetime.timedelta(days=50)
tao = 40.0/252.0
vol = 0.253768
spot = 1000
k = spot*1.05
call = BlackCalculator(tao,k,OptionType.CALL,spot,vol)
rho = 0.01

# print('d1 : ',call.D1)
print('Spot : ',spot)
print('Delta : ',call.Delta())

gamma = call.Gamma()
gamma_e = call.Gamma_1pct()
print('Gamma : ',gamma)
print('Gamma e: ',gamma_e)
tao = PricingUtil.get_ttm(dt_eval, mdt)
H = (1.5 * math.exp(-0.03*tao) * (1.0/1000.0) * spot * (gamma ** 2) / rho) ** (1 / 3)
H_1 = (1.5 * math.exp(-0.03*tao) * (1.0/1000.0) * spot * (gamma_e ** 2) / rho) ** (1 / 3)
print('H : ',H)
print('H 1 : ',H_1)

spot = 100
k = spot*1.05
call = BlackCalculator(tao,k,OptionType.CALL,spot,vol)
# print('d1 : ',call.D1)
print('Spot : ',spot)
print('Delta : ',call.Delta())

gamma = call.Gamma()
gamma_e = call.Gamma_1pct()
print('Gamma : ',gamma)
print('Gamma e: ',gamma_e)
tao = PricingUtil.get_ttm(dt_eval, mdt)
H = (1.5 * math.exp(-0.03*tao) * (1.0/1000.0) * spot * (gamma ** 2) / rho) ** (1 / 3)
H_1 = (1.5 * math.exp(-0.03*tao) * (1.0/1000.0) * spot * (gamma_e ** 2) / rho) ** (1 / 3)
print('H : ',H)
print('H 1 : ',H_1)

spot = 10
k = spot*1.05
call = BlackCalculator(tao,k,OptionType.CALL,spot,vol)
# print('d1 : ',call.D1)
print('Spot : ',spot)
print('Delta : ',call.Delta())

gamma = call.Gamma()
gamma_e = call.Gamma_1pct()
print('Gamma : ',gamma)
print('Gamma e: ',gamma_e)
tao = PricingUtil.get_ttm(dt_eval, mdt)
H = (1.5 * math.exp(-0.03*tao) * (1.0/1000.0) * spot * (gamma ** 2) / rho) ** (1 / 3)
H_1 = (1.5 * math.exp(-0.03*tao) * (1.0/1000.0) * spot * (gamma_e ** 2) / rho) ** (1 / 3)
print('H : ',H)
print('H 1 : ',H_1)

spot = 1
k = spot*1.05
call = BlackCalculator(tao,k,OptionType.CALL,spot,vol)
# print('d1 : ',call.D1)
print('Spot : ',spot)
print('Delta : ',call.Delta())

gamma = call.Gamma()
gamma_e = call.Gamma_1pct()
print('Gamma : ',gamma)
print('Gamma e: ',gamma_e)
tao = PricingUtil.get_ttm(dt_eval, mdt)
H = (1.5 * math.exp(-0.03*tao) * (1.0/1000.0) * spot * (gamma ** 2) / rho) ** (1 / 3)
H_1 = (1.5 * math.exp(-0.03*tao) * (1.0/1000.0) * spot * (gamma_e ** 2) / rho) ** (1 / 3)
print('H : ',H)
print('H 1 : ',H_1)