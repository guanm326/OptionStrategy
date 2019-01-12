import datetime
from back_test.model.base_account import BaseAccount
from back_test.model.base_future_coutinuous import BaseFutureCoutinuous
from back_test.model.base_instrument import BaseInstrument
from back_test.model.base_option_set import BaseOptionSet
from back_test.model.constant import Util, FrequentType, LongShort
import data_access.get_data as data

start_date = datetime.date(2017, 6, 1)
end_date = datetime.date(2017, 7, 1)
df_option_metrics = data.get_50option_mktdata(start_date, end_date)
df_index_metrics = data.get_index_mktdata(start_date, end_date, 'index_50etf')
df_cf = data.get_mktdata_future_c1_daily(start_date, end_date, 'ih')

optionset = BaseOptionSet(df_option_metrics)
optionset.init()
account = BaseAccount(Util.MILLION,rf=0)

def _next():
    optionset.next()

def value_equal(df,portfolio_value,cash,portfolio_margin_capital):
    if abs(df['portfolio_value'] - portfolio_value)>0.001:
        return False
    elif abs(df['portfolio_margin_capital'] - portfolio_margin_capital)>0.001:
        return False
    elif abs(df['cash'] - cash) > 0.001:
        return False
    else:
        return True


print('Option Trading Account Test')
maturity = optionset.select_maturity_date(nbr_maturity=0, min_holding=20)
list_atm_call, list_atm_put = optionset.get_options_list_by_moneyness_mthd1(
    moneyness_rank=0,
    maturity=maturity)
atm_call = optionset.select_higher_volume(list_atm_call)
atm_put = optionset.select_higher_volume(list_atm_put)

print('期权卖方开仓')
order = account.create_trade_order(atm_call, LongShort.SHORT, 10)
record = atm_call.execute_order(order)
account.add_record(record, atm_call)
account.daily_accounting(optionset.eval_date)
print('Test Equal: ',value_equal(account.account.loc[optionset.eval_date],999950,971070,31440))
print('-'*50)

_next()


print('加仓')
order = account.create_trade_order(atm_call, LongShort.SHORT, 2)
record = atm_call.execute_order(order)
account.add_record(record, atm_call)
account.daily_accounting(optionset.eval_date)
print('Test Equal: ',value_equal(account.account.loc[optionset.eval_date],1000660.0,968692.0,34176.00000000002))
print('-'*50)
_next()

print('减仓')
order = account.create_trade_order(atm_call, LongShort.LONG, 2)
record = atm_call.execute_order(order)
account.add_record(record, atm_call)
account.daily_accounting(optionset.eval_date)
print('Test Equal: ',value_equal(account.account.loc[optionset.eval_date],1001766.0,978262.0,24414.00000000002))
print('-'*50)
_next()

print('平仓')
order = account.create_trade_order(atm_call, LongShort.LONG, 10)
record = atm_call.execute_order(order)
account.add_record(record, atm_call)
account.daily_accounting(optionset.eval_date)
print('Test Equal: ',value_equal(account.account.loc[optionset.eval_date],1001376.0,1001376.0,0.0))
print('-'*50)
_next()

account.daily_accounting(optionset.eval_date)
print('-'*50)
print('Test Equal: ',value_equal(account.account.loc[optionset.eval_date],1001376.0,1001376.0,0.0))
print('-'*50)
_next()


print('期权买方开仓')
order = account.create_trade_order(atm_put, LongShort.LONG, 10)
record = atm_put.execute_order(order)
account.add_record(record, atm_put)
account.daily_accounting(optionset.eval_date)
print('Test Equal: ',value_equal(account.account.loc[optionset.eval_date],1001326.0,998286.0,0.0))
print('-'*50)
_next()
print('加仓')
order = account.create_trade_order(atm_put, LongShort.LONG, 2)
record = atm_put.execute_order(order)
account.add_record(record, atm_put)
account.daily_accounting(optionset.eval_date)
print('Test Equal: ',value_equal(account.account.loc[optionset.eval_date],1000916.0,997748.0,0.0))
print('-'*50)
_next()
print('减仓')

order = account.create_trade_order(atm_put, LongShort.SHORT, 8)
record = atm_put.execute_order(order)
account.add_record(record, atm_put)
account.daily_accounting(optionset.eval_date)
print('Test Equal: ',value_equal(account.account.loc[optionset.eval_date],1001104.0,999972.0,0.0))
print('-'*50)
_next()
print('平仓')
order = account.create_trade_order(atm_put, LongShort.SHORT, 4)
record = atm_put.execute_order(order)
account.add_record(record, atm_put)
account.daily_accounting(optionset.eval_date)
print('Test Equal: ',value_equal(account.account.loc[optionset.eval_date],1000976.0,1000976.0,0.0))
print('-'*50)


