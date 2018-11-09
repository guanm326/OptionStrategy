from back_test.model.base_option_set import BaseOptionSet
from back_test.model.base_option import BaseOption
from back_test.model.base_account import BaseAccount
from back_test.model.base_instrument import BaseInstrument
import data_access.get_data as get_data
import back_test.model.constant as c
import datetime
import numpy as np
from Utilities.PlotUtil import PlotUtil
import matplotlib.pyplot as plt
import pandas as pd
from OptionStrategyLib.VolatilityModel.historical_volatility import HistoricalVolatilityModels as histvol


def open_position(df_index, dt_date):
    if dt_date not in df_index.index:
        return False
    ma_5 = df_index.loc[dt_date, 'ma_5']
    ma_60 = df_index.loc[dt_date, 'ma_60']
    if ma_5 < ma_60:
        return True
    else:
        return False


def close_position(df_index, strategy_res, dt_date):
    dt_maturity = None
    for option in strategy_res.keys():
        if option is not None:
            dt_maturity = option.maturitydt()
    if (dt_maturity - optionset.eval_date).days <= 5:
        return True
    ma_5 = df_index.loc[dt_date, 'ma_5']
    ma_60 = df_index.loc[dt_date, 'ma_60']
    if ma_5 > ma_60:
        return True
    else:
        return False


def collar():
    name = 'collar'
    maturity0 = optionset.select_maturity_date(nbr_maturity=0, min_holding=20)
    maturity1 = optionset.select_maturity_date(nbr_maturity=1, min_holding=20)

    list_call, xx = optionset.get_options_list_by_moneyness_mthd1(moneyness_rank=-2,
                                                                  maturity=maturity0,
                                                                  cd_price=c.CdPriceType.OPEN)
    xxx, list_put = optionset.get_options_list_by_moneyness_mthd1(moneyness_rank=-2,
                                                                  maturity=maturity1,
                                                                  cd_price=c.CdPriceType.OPEN)
    call = optionset.select_higher_volume(list_call)
    put = optionset.select_higher_volume(list_put)
    if put is None:
        xxx, list_put = optionset.get_options_list_by_moneyness_mthd1(moneyness_rank=0,
                                                                      maturity=maturity1,
                                                                      cd_price=c.CdPriceType.OPEN)
        put = optionset.select_higher_volume(list_put)
    # res = {call: c.LongShort.SHORT, put: c.LongShort.LONG}
    return [call,put],name

def bull_spread():
    name = 'bull_spread'
    maturity = optionset.select_maturity_date(nbr_maturity=0, min_holding=min_holding)

    xx, list_put0 = optionset.get_options_list_by_moneyness_mthd1(moneyness_rank=0,
                                                                  maturity=maturity,
                                                                  cd_price=c.CdPriceType.OPEN)
    xxx, list_put2 = optionset.get_options_list_by_moneyness_mthd1(moneyness_rank=-2,
                                                                  maturity=maturity,
                                                                  cd_price=c.CdPriceType.OPEN)
    put_long = optionset.select_higher_volume(list_put0)
    put_short = optionset.select_higher_volume(list_put2)
    # res = {put0: c.LongShort.LONG, put2: c.LongShort.SHORT}
    return [put_long,put_short],name

def bull_spread_vol(dt_date):
    name = 'bull_spread_vol'
    maturity = optionset.select_maturity_date(nbr_maturity=0, min_holding=min_holding)
    xx, list_put0 = optionset.get_options_list_by_moneyness_mthd1(moneyness_rank=0,
                                                                  maturity=maturity,
                                                                  cd_price=c.CdPriceType.OPEN)
    put_long = optionset.select_higher_volume(list_put0)
    # if put_long is None:
    #     xxx, list_put0 = optionset.get_options_list_by_moneyness_mthd1(moneyness_rank=0,
    #                                                                   maturity=maturity,
    #                                                                   cd_price=c.CdPriceType.OPEN)
    #     put_long = optionset.select_higher_volume(list_put0)
    std_close = df_index1.loc[dt_date,'std_close']
    k_target = put_long.strike()-std_close
    put_short = optionset.select_higher_volume(optionset.get_option_closest_strike(c.OptionType.PUT, k_target, maturity))
    return [put_long,put_short],name

def three_way(dt_date):
    name = 'three_way'
    maturity = optionset.select_maturity_date(nbr_maturity=0, min_holding=20)
    xxx, list_put0 = optionset.get_options_list_by_moneyness_mthd1(moneyness_rank=0,
                                                                  maturity=maturity,
                                                                  cd_price=c.CdPriceType.OPEN)
    put_long = optionset.select_higher_volume(list_put0)
    std_close = df_index1.loc[dt_date, 'std_close']
    k_low = np.floor(put_long.strike() - std_close)
    put_short = optionset.select_higher_volume(optionset.get_option_by_strike(c.OptionType.PUT, k_low, maturity))
    k_high = np.floor(put_long.strike() + std_close)
    call_short = optionset.select_higher_volume(optionset.get_option_by_strike(c.OptionType.CALL, k_high, maturity))
    return [put_long,put_short,call_short],name

def buy_put():
    name = 'buy_put'
    maturity = optionset.select_maturity_date(nbr_maturity=0, min_holding=min_holding)

    xx, list_put0 = optionset.get_options_list_by_moneyness_mthd1(moneyness_rank=-2,
                                                                  maturity=maturity,
                                                                  cd_price=c.CdPriceType.OPEN)
    put = optionset.select_higher_volume(list_put0)
    if put is None:
        xxx, list_put = optionset.get_options_list_by_moneyness_mthd1(moneyness_rank=0,
                                                                      maturity=maturity,
                                                                      cd_price=c.CdPriceType.OPEN)
        put = optionset.select_higher_volume(list_put)
    return [put],name

def excute(strategy_res, unit_index):
    for option in strategy_res.keys():
        if option is None:
            continue
        unit = unit_index / option.multiplier()
        order = account.create_trade_order(option, strategy_res[option], unit, cd_trade_price=cd_trade_price)
        record = option.execute_order(order, slippage=slippage)
        account.add_record(record, option)

def excute_delta(strategy_res, unit_index):
    delta = 0
    multiplier = None
    for option in strategy_res.keys():
        if option is None:
            continue
        delta += option.get_delta(option.get_implied_vol())*strategy_res[option].value
        multiplier = option.multiplier()
    unit = unit_index / multiplier/abs(delta)
    for option in strategy_res.keys():
        if option is None:
            continue
        order = account.create_trade_order(option, strategy_res[option], unit, cd_trade_price=cd_trade_price)
        record = option.execute_order(order, slippage=slippage)
        account.add_record(record, option)


def close_all_options(account):
    for option in account.dict_holding.values():
        if isinstance(option, BaseOption):
            order = account.create_close_order(option, cd_trade_price=cd_trade_price)
            record = option.execute_order(order, slippage=slippage)
            account.add_record(record, option)

def shift_bull_spread(option_long,option_short,spot):
    if option_short is None:
        maturity = optionset.select_maturity_date(nbr_maturity=0, min_holding=20)
        xxx, list_put2 = optionset.get_options_list_by_moneyness_mthd1(moneyness_rank=-2,
                                                                       maturity=maturity,
                                                                       cd_price=c.CdPriceType.OPEN)
        put2 = optionset.select_higher_volume(list_put2)
        if put2 is None:
            return False
        else:
            print(optionset.eval_date,' shift')
            return True
    else:
        if spot < option_long.strike():
            print(optionset.eval_date, ' shift')
            return True
        else:
            return False

def shift_bull_spread_vol(option_long,option_short,spot,dt_date):
    if option_short is None:
        return False
        # maturity = optionset.select_maturity_date(nbr_maturity=0, min_holding=1)
        # std_close = df_index1.loc[dt_date, 'std_close']
        # k_target = put_long.strike() - std_close
        # put_short = optionset.select_higher_volume(optionset.get_option_closest_strike(c.OptionType.PUT, k_target, maturity))
        # if put_short is None:
        #     return False
        # else:
        #     print(optionset.eval_date,' shift')
        #     return True
    else:
        if spot <= (option_long.strike()+option_short.strike())/2:
        # if spot <= option_short.strike():
            print(optionset.eval_date, ' shift')
            return True
        else:
            return False

def shift_buy_put(put,spot):
    if spot <= put.strike():
        return True

def shift_collar(call,put,spot):
    k_call = call.strike()
    k_put = put.strike()
    if call is None:
        maturity = optionset.select_maturity_date(nbr_maturity=0, min_holding=20)
        list_call, xxx = optionset.get_options_list_by_moneyness_mthd1(moneyness_rank=-2,
                                                                       maturity=maturity,
                                                                       cd_price=c.CdPriceType.OPEN)
        call = optionset.select_higher_volume(list_call)
        if call is None:
            return False
        else:
            print(optionset.eval_date,' shift')
            return True
    else:
        if k_call - spot <= 0.05 or k_put >= spot:
            print(optionset.eval_date, ' shift')
            return True
        else:
            return False

def shift_three_way(put_long,put_short,call_short,spot,dt_date):
    if put_short is None or call_short is None:
        maturity = optionset.select_maturity_date(nbr_maturity=0, min_holding=20)
        std_close = df_index1.loc[dt_date, 'std_close']
        k_low = np.floor(put_long.strike() - std_close)
        put_short = optionset.select_higher_volume(optionset.get_option_by_strike(c.OptionType.PUT, k_low, maturity))
        k_high = np.floor(put_long.strike() + std_close)
        call_short = optionset.select_higher_volume(optionset.get_option_by_strike(c.OptionType.CALL, k_high, maturity))
        if call_short is not None and put_short is not None:
            return True
        else:
            return False
    else:
        if spot > call_short.strike() or spot < put_short.strike():
            return True
        else:
            return False


start_date = datetime.date(2015, 1, 1)
end_date = datetime.date(2018, 11, 1)
dt_histvol = start_date - datetime.timedelta(days=500)
min_holding = 20
init_fund = c.Util.BILLION
slippage = 0
cd_trade_price = c.CdTradePrice.VOLUME_WEIGHTED
df_metrics = get_data.get_50option_mktdata(start_date, end_date)
df_index = get_data.get_index_mktdata(dt_histvol, end_date, c.Util.STR_INDEX_50ETF)
df_index['ma_5'] = c.Statistics.moving_average(df_index[c.Util.AMT_CLOSE], n=5).shift()
df_index['ma_60'] = c.Statistics.moving_average(df_index[c.Util.AMT_CLOSE], n=60).shift()
df_index['ma_120'] = c.Statistics.moving_average(df_index[c.Util.AMT_CLOSE], n=120).shift()
df_index['std_close'] = c.Statistics.standard_deviation(df_index[c.Util.AMT_CLOSE], n=20).shift()
df_index['histvol_20'] = histvol.hist_vol(df_index[c.Util.AMT_CLOSE]).shift()
df_index.to_csv('../../accounts_data/df_index.csv')
dt_start = max(df_metrics[c.Util.DT_DATE].values[0], df_index[c.Util.DT_DATE].values[0])
df_metrics = df_metrics[df_metrics[c.Util.DT_DATE] >= dt_start].reset_index(drop=True)
df_index = df_index[df_index[c.Util.DT_DATE] >= dt_start].reset_index(drop=True)
optionset = BaseOptionSet(df_metrics)
index = BaseInstrument(df_index)
optionset.init()
index.init()
account = BaseAccount(init_fund=c.Util.BILLION, leverage=1.0, rf=0.03)
df_index1 = df_index.set_index(c.Util.DT_DATE)

# 标的指数开仓
unit_index = np.floor(account.cash / index.mktprice_close() / index.multiplier())
option_shares = unit_index
order_index = account.create_trade_order(index, c.LongShort.LONG, unit_index, cd_trade_price=c.CdTradePrice.CLOSE)
record_index = index.execute_order(order_index, slippage=slippage)
account.add_record(record_index, index)

df_holding_period = pd.DataFrame()
name = ''
empty_position = True
unit_p = None
unit_c = None
strategy_res = None
init_index = df_index[c.Util.AMT_CLOSE].values[0]
base_npv = []
maturity1 = optionset.select_maturity_date(nbr_maturity=0, min_holding=min_holding)
while optionset.eval_date <= end_date:
    if maturity1 > end_date:  # Final close out all.
        close_out_orders = account.creat_close_out_order()
        for order in close_out_orders:
            execution_record = account.dict_holding[order.id_instrument]\
                .execute_order(order, slippage=0,execute_type=c.ExecuteType.EXECUTE_ALL_UNITS)
            account.add_record(execution_record, account.dict_holding[order.id_instrument])
        account.daily_accounting(optionset.eval_date)
        base_npv.append(index.mktprice_close() / init_index)
        print(optionset.eval_date, ' close out ')
        break

    # 平仓/移仓
    if not empty_position:
        # if close_position(df_index1, strategy_res, optionset.eval_date) \
        #         or shift_bull_spread(put_long, put_short, index.mktprice_last_close()):
        if close_position(df_index1, strategy_res, optionset.eval_date) \
                or shift_bull_spread_vol(put_long,put_short,index.mktprice_last_close(),index.eval_date):
        # if close_position(df_index1, strategy_res, optionset.eval_date) \
        #         or shift_three_way(put_long,put_short,call_short,index.mktprice_last_close(),index.eval_date):
        # if close_position(df_index1, strategy_res, optionset.eval_date) \
        #         or shift_buy_put(put,index.mktprice_last_close()):
            close_all_options(account)
            empty_position = True

    # 开仓
    if empty_position and open_position(df_index1, optionset.eval_date):
        # [put_long, put_short], name = bull_spread()  # TODO: OPTION STRATEGY
        # strategy_res = {put_short: c.LongShort.SHORT, put_long: c.LongShort.LONG}
        [put_long, put_short],name = bull_spread_vol(index.eval_date) # TODO: OPTION STRATEGY
        strategy_res = {put_short:c.LongShort.SHORT,put_long:c.LongShort.LONG}
        # [put_long,put_short,call_short],name = three_way(index.eval_date) # TODO: OPTION STRATEGY
        # strategy_res = {put_short:c.LongShort.SHORT,put_long:c.LongShort.LONG,call_short:c.LongShort.SHORT}
        # [put], name = buy_put()  # TODO: OPTION STRATEGY
        # strategy_res = {put: c.LongShort.LONG}
        excute(strategy_res, unit_index)
        empty_position = False

    account.daily_accounting(optionset.eval_date)
    base_npv.append(index.mktprice_close()/init_index)
    if not optionset.has_next(): break
    optionset.next()
    index.next()

res = account.analysis()
print(res)
account.account['base_npv'] = base_npv
account.account.to_csv('../../accounts_data/hedge_by_option_account_1--'+name+'.csv')
account.trade_records.to_csv('../../accounts_data/hedge_by_option_records_1--'+name+'.csv')

pu = PlotUtil()
dates = list(account.account.index)
hedged_npv = list(account.account[c.Util.PORTFOLIO_NPV])
pu.plot_line_chart(dates, [hedged_npv, base_npv], ['hedged_npv', 'base_npv'])

plt.show()
