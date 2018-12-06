from back_test.model.constant import QuantlibUtil as ql_util
import datetime


t = ql_util.get_business_between(datetime.date(2018,1,1),datetime.date(2018,1,15))
print(t)