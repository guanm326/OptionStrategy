import datetime
from back_test.model.base_account import BaseAccount
from back_test.model.base_future_set import BaseFutureSet
from back_test.model.base_future import BaseFuture
from back_test.model.base_future_coutinuous import BaseFutureCoutinuous
from back_test.model.constant import Util, FrequentType, LongShort
import data_access.get_data as data

start_date = datetime.date(2017, 6, 1)
end_date = datetime.date(2017, 12, 1)

df_cf = data.get_mktdata_future_daily(start_date, end_date, 'ih')
df_cf1 = data.get_mktdata_future_c1_daily(start_date,end_date,'ih')

future = BaseFuture(df_cf1)
future.init()
futureset = BaseFutureSet(df_cf)
futureset.init()
account = BaseAccount(Util.MILLION*10,rf=0)

print('Future Set Test')
contracts = futureset.eligible_futures
c_1 = futureset.select_higher_volume(contracts)
order = account.create_trade_order(c_1, LongShort.LONG, 10)
record = c_1.execute_order(order)
account.add_record(record, c_1)

while futureset.has_next():
    if not c_1.has_next():
        print(futureset.eval_date)
        order = account.create_trade_order(c_1, LongShort.SHORT, 10)
        record = c_1.execute_order(order)
        account.add_record(record, c_1)
        contracts = futureset.eligible_futures
        c_1 = futureset.select_higher_volume(contracts)
        print(c_1.id_instrument())
        order = account.create_trade_order(c_1, LongShort.LONG, 10)
        record = c_1.execute_order(order)
        account.add_record(record, c_1)
    account.daily_accounting(futureset.eval_date)
    futureset.next()
print(account.analysis())
print(account.trade_records)
"""
accumulate_yield     0.098943
annual_yield         0.207676
annual_volatility    0.094362
max_drawdown        -0.042301
prob_of_win(D)       0.523810
win_loss_ratio       1.301487
sharpe               2.200838
Calmar               4.909454
turnover             1.655823
avg_margin           0.113584
max_margin           0.118410
"""

future_continuous = BaseFutureCoutinuous(df_future_c1=df_cf1,df_futures_all_daily=df_cf)
future_continuous.init()
account = BaseAccount(Util.MILLION*10,rf=0)

order = account.create_trade_order(future_continuous, LongShort.LONG, 10)
record = future_continuous.execute_order(order)
account.add_record(record, future_continuous)
account.daily_accounting(future_continuous.eval_date)
future_continuous.next()

print('Future continuous Test')

while future_continuous.has_next():
    if not c_1.has_next():
        if future_continuous.shift_contract_month(account,0):
            print(future_continuous.eval_date)
            print(future_continuous.id_future)
    account.daily_accounting(future_continuous.eval_date)
    future_continuous.next()
print(account.analysis())
print(account.trade_records)

"""
accumulate_yield     0.102948
annual_yield         0.216495
annual_volatility    0.096098
max_drawdown        -0.042154
prob_of_win(D)       0.531746
win_loss_ratio       1.266389
sharpe               2.252856
Calmar               5.135783
turnover             1.649377
avg_margin           0.113898
max_margin           0.117998
"""

