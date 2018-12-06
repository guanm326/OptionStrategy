import pandas as pd
import numpy as np

def get_strike_interval(strike):
    """
    给定行权价，返回其上下两个行权价之间平均间隔
    :param strike: 标准合约行权价，不能是 2.847 这种调整过的行权价
    :return:
    """
    if strike < 3:
        return 0.05
    elif strike == 3:
        return 0.075
    elif 3 < strike < 5:
        return 0.1
    elif strike == 5:
        return 0.175
    elif 5 < strike < 10:
        return 0.25
    elif strike == 10:
        return 0.375
    elif 10 < strike < 20:
        return 0.5
    elif strike == 20:
        return 0.75
    elif 20 < strike < 50:
        return 1
    elif strike == 50:
        return 1.75
    elif 50 < strike < 100:
        return 2.5
    elif strike == 100:
        return 3.75
    else:
        return 5



def add_ivix(data):
    """
    计算每日 ivix,skew指标
    :param data: DataFrame 当日所有期权数据,以 ticker,Tdate 为Multiindex
    :return: DataFrame 添加了 ivix,skew 两列数据的原数据
    """
    data_ivix = data.loc[(data['series'].isin([1, 2, 3])) & (data['dividend'] == 0),
                         ['close', 'call_or_put', 'strike', 'strike_date', 'R_avg7', 'series']].copy()  # 只用未经过标准合约计算
    data_ivix.reset_index(inplace=True)
    data_ivix.set_index('strike', inplace=True)  # 更改 index 为行权价 strike,并排序
    data_ivix.sort_index(inplace=True)
    r_avg7 = data_ivix['R_avg7'].iloc[0] / 100  # 无风险利率
    current_date = data['Tdate'].iloc[0]  # 当前日期
    t = []  # 当月和次月距离到期日时间，年化
    sigma = []  # 当月和次月计算得到的 sigma 平方
    skew = []  # 当月和次月计算得到的 S
    i = 1
    while len(t) < 2:
        data_ivix_ = data_ivix[data_ivix['series'] == i].copy()
        strike_date = data_ivix_['strike_date'].iloc[0]
        res_time = (pd.to_datetime(strike_date) - current_date).days / 365
        if res_time == 0:  # 到期日最后一天收盘，当月和次月要切换到 2,3
            i += 1
            data_ivix_ = data_ivix[data_ivix['series'] == i].copy()
            strike_date = data_ivix_['strike_date'].iloc[0]
            res_time = (pd.to_datetime(strike_date) - current_date).days / 365
        i += 1
        t.append(res_time)
        data_ivix1 = data_ivix_.loc[data_ivix_['call_or_put'] == 'C', ['close']].copy()  # 更改数据结构，方便对应行权价合约价格相减等
        data_ivix1=data_ivix1.rename(columns={'close': 'call_close'})
        data_ivix1['put_close'] = data_ivix_[data_ivix_['call_or_put'] == 'P']['close']
        data_ivix1['diff'] = abs(data_ivix1['call_close'] - data_ivix1['put_close'])

        ms_strike = data_ivix1['diff'].idxmin()  # 看涨和看跌合约价格差的绝对值最小对应的行权价
        forward_price = ms_strike + np.exp(r_avg7 * res_time) * (data_ivix1.loc[ms_strike, 'call_close'] - data_ivix1.loc[ms_strike, 'put_close'])
        try:  # 低于 forward_price 的行权价，极端情况可能在行权价序列两端
            k0 = next(x for x in data_ivix1.index.sort_values(ascending=False) if x <= forward_price)
        except StopIteration:
            k0 = data_ivix1.index[0]
        data_ivix11 = pd.concat([data_ivix_[(data_ivix_['call_or_put'] == 'P') & (data_ivix_.index <= k0)][['close']].tail(10),
                                 data_ivix_[(data_ivix_['call_or_put'] == 'C') & (data_ivix_.index >= k0)][['close']].head(10)], axis=0)
        data_ivix11 = data_ivix11.groupby(data_ivix11.index).mean()  # 相同行权价的平均值，这里应该只有等于 k0 的行权价有两个合约
        data_ivix11['dk'] = [get_strike_interval(x) for x in data_ivix11.index]  # 行权价间隔
        # 其他计算 ivix,skew 中所需数据
        data_ivix11['contribution'] = data_ivix11['dk'] * np.exp(r_avg7 * res_time) * data_ivix11['close'] / data_ivix11.index ** 2
        sigma2 = data_ivix11['contribution'].sum() * 2 / res_time - (forward_price / k0 - 1) ** 2 / res_time
        sigma.append(sigma2)
        e1 = -(1 + np.log(forward_price / k0) - forward_price / k0)
        e2 = 2 * np.log(forward_price / k0) * (forward_price / k0 - 1) + 0.5 * np.log(forward_price / k0) ** 2
        e3 = 3 * (np.log(forward_price / k0) ** 2) * (1 / 3 * np.log(forward_price / k0) + forward_price / k0 - 1)
        data_ivix11['con1'] = data_ivix11['dk'] * data_ivix11['close'] / data_ivix11.index ** 2
        data_ivix11['con2'] = 2 * (1 - np.log(data_ivix11.index / forward_price)) * data_ivix11['dk'] * data_ivix11['close'] / data_ivix11.index ** 2
        data_ivix11['con3'] = 3 * (2 * np.log(data_ivix11.index / forward_price)
                                   - np.log(data_ivix11.index / forward_price) ** 2) * data_ivix11['dk'] * data_ivix11['close'] / data_ivix11.index ** 2
        p1 = -1 * np.exp(r_avg7 * res_time) * data_ivix11['con1'].sum() + e1
        p2 = np.exp(r_avg7 * res_time) * data_ivix11['con2'].sum() + e2
        p3 = np.exp(r_avg7 * res_time) * data_ivix11['con3'].sum() + e3
        skew_s = (p3 - 3 * p1 * p2 + 2 * p1 ** 3) / (p2 - p1 ** 2)**1.5

        skew.append(skew_s)
    t1, t2 = t
    s1, s2 = sigma
    skew_s1, skew_s2 = skew
    w1 = (t2-30/365)/(t2-t1)
    data['ivix'] = 100 * np.sqrt(np.round((t1 * s1 * w1 + t2 * s2 * (1-w1)) * 365/30, 8))
    data['skew'] = 100 - 10 * (w1 * skew_s1 + (1 - w1) * skew_s2)
    return data

df = pd.read_excel('../../data/daily_option.xlsx')
res = add_ivix(df)
print(res)