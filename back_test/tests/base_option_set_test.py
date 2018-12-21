import datetime
from data_access.get_data import get_50option_mktdata, get_50option_minute_with_underlying
from back_test.model.base_option_set import BaseOptionSet
import pandas as pd
import back_test.model.constant as c

start_date = datetime.date(2015, 2, 9)
end_date = datetime.date.today()
# df_metrics=pd.read_excel('../../data/df_metrics.xlsx')
# df_metrics[c.Util.DT_DATE] = df_metrics[c.Util.DT_DATE].apply(lambda x: x.date())
# df_metrics[c.Util.DT_MATURITY] = df_metrics[c.Util.DT_MATURITY].apply(lambda x: x.date())
df_metrics = get_50option_mktdata(start_date, end_date)
df_metrics.to_excel('../../data/df_metrics.xlsx')
optionset = BaseOptionSet(df_metrics)
optionset.init()
while optionset.has_next():
    # if optionset.eval_date == datetime.date(2018,4,27):
    #     print('')
    optionset.next()
