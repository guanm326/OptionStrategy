from OptionStrategyLib.OptionStrategy.protective_put.hedging import *


start_date = datetime.date(2015, 1, 1)
end_date = datetime.date(2018, 11, 1)
dt_histvol = start_date - datetime.timedelta(days=500)
init_fund = c.Util.BILLION

df_metrics = get_data.get_50option_mktdata(start_date, end_date)
df_index = get_data.get_index_mktdata(dt_histvol, end_date, c.Util.STR_INDEX_50ETF)
df_index = signal(df_index)

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
        if close_position(df_index1, strategy_res, optionset) \
                or shift_bull_spread_vol(put_long,put_short,index.mktprice_last_close(),optionset):
            close_all_options(account)
            empty_position = True

    # 开仓
    if empty_position and open_position(df_index1, optionset):
        [put_long, put_short],name = bull_spread_vol(df_index1,optionset,index.mktprice_open())
        strategy_res = {put_short:c.LongShort.SHORT,put_long:c.LongShort.LONG}
        excute(strategy_res, unit_index,account)
        empty_position = False

    account.daily_accounting(optionset.eval_date)
    base_npv.append(index.mktprice_close()/init_index)
    if not optionset.has_next(): break
    optionset.next()
    index.next()

res = account.analysis()
print(res)
account.account['base_npv'] = base_npv
account.account.to_csv('../../accounts_data/hedge_by_option_account_'+name+'_1.csv')
account.trade_records.to_csv('../../accounts_data/hedge_by_option_records_'+name+'_1.csv')

pu = PlotUtil()
dates = list(account.account.index)
hedged_npv = list(account.account[c.Util.PORTFOLIO_NPV])
pu.plot_line_chart(dates, [hedged_npv, base_npv], ['hedged_npv', 'base_npv'])

plt.show()
