import datetime
import matplotlib.pyplot as plt
import back_test.model.constant as c
import data_access.get_data as get_data
from Utilities.PlotUtil import PlotUtil
from Strategy.model.VolTrading_HvIvSignal import VolTrading

"""
隐含与历史波动率策略报告原版参数设定：
    self.min_holding = 20
    self.slippage = 0
    self.nbr_maturity = 0
    self.moneyness_rank = 0
    self.m = 1
    self.rf = 0.03
    self.h = 90
    self.n_hv = 20
    self.n_cloese_by_maturity = 5
    self.min_premium = 0 # 对冲成本对应的开平仓最低隐含波动率溢价
    dt_start = datetime.date(2016, 12, 31)
    dt_end = datetime.date(2017, 12, 31)
结果：
    accumulate_yield     0.057487
    annual_yield         0.059427
    annual_volatility    0.016836
    max_drawdown        -0.010365
    prob_of_win(D)       0.815574
    win_loss_ratio       0.490094
    sharpe               2.104261
    Calmar               5.733450
    turnover             2.025159
"""

dt_start = datetime.date(2016, 12, 31)
dt_end = datetime.date(2017, 12, 31)
dt_histvol = dt_start - datetime.timedelta(days=300)
name_code = c.Util.STR_IH
name_code_option = c.Util.STR_50ETF
df_metrics = get_data.get_50option_mktdata(dt_start, dt_end)
df_future_c1_daily = get_data.get_mktdata_future_c1_daily(dt_histvol, dt_end, name_code)
df_futures_all_daily = get_data.get_mktdata_future_daily(dt_start, dt_end, name_code)
df_iv = get_data.get_iv_by_moneyness(dt_histvol, dt_end, name_code_option)
df_iv = df_iv[df_iv[c.Util.CD_OPTION_TYPE] == 'put_call_htbr'][[c.Util.DT_DATE, c.Util.PCT_IMPLIED_VOL]].reset_index(
    drop=True)


class VolTradingIvHv(VolTrading):
    def __init__(self, dt_start, dt_end, df_metrics, df_iv, df_future_c1_daily, df_futures_all_daily):
        super().__init__(dt_start, dt_end, df_metrics, df_iv, df_future_c1_daily, df_futures_all_daily)
        self.min_holding = 20
        self.slippage = 0
        self.nbr_maturity = 0
        self.moneyness_rank = 0
        self.m_notional = 1
        self.rf = 0.03
        self.n_premium_std = 90
        self.n_hv = 20
        self.n_cloese_by_maturity = 5
        self.min_premium = 0.0 / 100.0

    def open_signal(self):
        return self.open_signal_ivhv()

    def close_signal(self):
        return self.close_signal_maturity() or self.close_signal_ivhv()


vol_arbitrage = VolTradingIvHv(dt_start, dt_end, df_metrics, df_iv, df_future_c1_daily, df_futures_all_daily)

vol_arbitrage.init()
account = vol_arbitrage.back_test()

# account.account.to_csv('../iv_hv_account-test.csv')
# account.trade_records.to_csv('../iv_hv_record-test.csv')
print('-' * 50)
res = account.analysis()
# print(res)
print('TEST CASE ')
print('-' * 50)
if abs(res['accumulate_yield'] - 0.057487) < 0.0001:
    print('SUCCESSFUL! TEST PASSED, VALUE EQUAL !')
else:
    print('FAILED')
