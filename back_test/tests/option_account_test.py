import datetime

from back_test.model.base_account import BaseAccount
from back_test.model.base_future_coutinuous import BaseFutureCoutinuous
from back_test.model.base_instrument import BaseInstrument
from back_test.model.base_option_set import BaseOptionSet
from back_test.model.constant import TradeType, Util, FrequentType, LongShort
from back_test.model.trade import Trade
import data_access.get_data as data

start_date = datetime.date(2017, 6, 1)
end_date = datetime.date(2017, 7, 1)

df_option_metrics = data.get_50option_mktdata(start_date, end_date)
df_index_metrics = data.get_index_mktdata(start_date, end_date, 'index_50etf')
df_cf = data.get_mktdata_future_c1_daily(start_date, end_date, 'ih')



optionset = BaseOptionSet(df_option_metrics)
optionset.init()
instrument = BaseInstrument(df_index_metrics)
instrument.init()
future = BaseFutureCoutinuous(df_cf, df_cf, frequency=FrequentType.DAILY)
future.init()
account = BaseAccount(Util.MILLION,rf=0)
def _next():
    optionset.next()
    instrument.next()
    future.next()
# print('开仓')
# order = account.create_trade_order(future,
#                                    LongShort.LONG,
#                                    10)
# execution_res = future.execute_order(order)
# account.add_record(execution_res, future)
# account.daily_accounting(future.eval_date)
# _next()
# print('加仓')
# order = account.create_trade_order(future,
#                                    LongShort.LONG,
#                                    5)
# execution_res = future.execute_order(order)
# account.add_record(execution_res, future)
# account.daily_accounting(future.eval_date)
# _next()
# print('减仓')
# order = account.create_trade_order(future,
#                                    LongShort.SHORT,
#                                    10)
# execution_res = future.execute_order(order)
# account.add_record(execution_res, future)
# account.daily_accounting(future.eval_date)
# _next()
# print('平仓')
# order = account.create_trade_order(future,
#                                    LongShort.SHORT,
#                                    5)
# execution_res = future.execute_order(order)
# account.add_record(execution_res, future)
# account.daily_accounting(future.eval_date)

print('option')
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
_next()


print('加仓')
order = account.create_trade_order(atm_call, LongShort.SHORT, 2)
record = atm_call.execute_order(order)
account.add_record(record, atm_call)
account.daily_accounting(optionset.eval_date)
_next()

print('减仓')
order = account.create_trade_order(atm_call, LongShort.LONG, 2)
record = atm_call.execute_order(order)
account.add_record(record, atm_call)
account.daily_accounting(optionset.eval_date)
_next()

print('平仓')
order = account.create_trade_order(atm_call, LongShort.LONG, 10)
record = atm_call.execute_order(order)
account.add_record(record, atm_call)
account.daily_accounting(optionset.eval_date)
_next()

account.daily_accounting(optionset.eval_date)
_next()

account.daily_accounting(optionset.eval_date)
_next()

print('期权买方开仓')
order = account.create_trade_order(atm_put, LongShort.LONG, 10)
record = atm_put.execute_order(order)
account.add_record(record, atm_put)
account.daily_accounting(optionset.eval_date)
_next()
print('加仓')
order = account.create_trade_order(atm_put, LongShort.LONG, 2)
record = atm_put.execute_order(order)
account.add_record(record, atm_put)
account.daily_accounting(future.eval_date)
_next()
print('减仓')

order = account.create_trade_order(atm_put, LongShort.SHORT, 8)
record = atm_put.execute_order(order)
account.add_record(record, atm_put)
account.daily_accounting(optionset.eval_date)

print('平仓')
order = account.create_trade_order(atm_put, LongShort.SHORT, 4)
record = atm_put.execute_order(order)
account.add_record(record, atm_put)
account.daily_accounting(optionset.eval_date)

print('account')
print(account.account)
print('trade_records')
print(account.trade_records)
print('analysis')
print(account.analysis())
print('final npv is 0.8054465845867517, and returns ',account.account[Util.PORTFOLIO_NPV].values[-1])
print('final cash is 791716.0252753928, and returns ',account.account[Util.CASH].values[-1])

# account.account.to_csv('account.csv')
# account.trade_records.to_csv('trade_records.csv')