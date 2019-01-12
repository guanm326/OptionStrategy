import datetime
from back_test.model.base_account import BaseAccount
from back_test.model.base_future_set import BaseFutureSet
from back_test.model.base_future import BaseFuture
from back_test.model.constant import Util, FrequentType, LongShort
import data_access.get_data as data

start_date = datetime.date(2017, 6, 1)
end_date = datetime.date(2017, 7, 1)

df_cf = data.get_mktdata_future_daily(start_date, end_date, 'ih')
df_cf1 = data.get_mktdata_future_c1_daily(start_date,end_date,'ih')

future = BaseFuture(df_cf1)
future.init()
futureset = BaseFutureSet(df_cf)
futureset.init()
account = BaseAccount(Util.MILLION,rf=0)

def _next():
    futureset.next()
    future.next()

def value_equal(df,portfolio_value,cash,portfolio_margin_capital):
    if abs(df['portfolio_value'] - portfolio_value)>0.001:
        return False
    elif abs(df['portfolio_margin_capital'] - portfolio_margin_capital)>0.001:
        return False
    elif abs(df['cash'] - cash) > 0.001:
        return False
    else:
        return True


print('Future Set Test')
contracts = futureset.eligible_futures
c_1 = futureset.select_higher_volume(contracts)
order = account.create_trade_order(c_1, LongShort.SHORT, 10)
record = c_1.execute_order(order)
account.add_record(record, c_1)
account.daily_accounting(futureset.eval_date)
print('-'*50)
print('date : ',futureset.eval_date)
print('portfolio_value : ',account.account.loc[futureset.eval_date,'portfolio_value'])
print('cash',account.account.loc[futureset.eval_date,'cash'])
print('portfolio_margin_capital',account.account.loc[futureset.eval_date,'portfolio_margin_capital'])
# print('Test Equal: ',value_equal(account.account.loc[futureset.eval_date],999950,971070,31440))
print('-'*50)

