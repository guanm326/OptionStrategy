import pandas as pd

from back_test.model.base_product import BaseProduct
from back_test.model.constant import FrequentType, Util, ExecuteType, LongShort
from back_test.model.trade import Order
from typing import Union


class BaseInstrument(BaseProduct):
    """
    BaseInstrument: STOCK/ETF/INDEX
    """

    def __init__(self, df_data: pd.DataFrame, df_daily_data: pd.DataFrame = None,
                 rf: float = 0.03, frequency: FrequentType = FrequentType.DAILY):
        super().__init__(df_data, df_daily_data, rf, frequency)
        self._multiplier = 1.0
        self.fee_rate = 0.0
        self.fee_per_unit = 0.0
        self._margin_rate = 1.0

    def __repr__(self) -> str:
        return 'BaseInstrument(id_instrument: {0},eval_date: {1},frequency: {2})' \
            .format(self.id_instrument(), self.eval_date, self.frequency)

    def margin_rate(self) -> Union[float, None]:
        return self._margin_rate

    def get_fund_required(self, long_short: LongShort) -> float:
        if long_short == LongShort.LONG:
            return self.mktprice_close()*self.multiplier()
        else:
            return self.get_initial_margin(long_short)

    def get_initial_margin(self,long_short:LongShort) -> Union[float, None]:
        if long_short == LongShort.LONG: margin = 0.0
        else:
            margin = self.mktprice_close() * self._margin_rate * self._multiplier # 假设可以融券的情况下
        return margin

    def get_maintain_margin(self,long_short:LongShort) -> Union[float, None]:
        if long_short == LongShort.LONG: margin = 0.0
        else:
            margin = self.mktprice_close() * self._margin_rate * self._multiplier
        return margin

    """ Long position only in base instrument. """

    def execute_order(self, order: Order, slippage=0,slippage_rate=0.0, execute_type: ExecuteType = ExecuteType.EXECUTE_ALL_UNITS):
        if order is None or order.trade_unit == 0: return
        # if execute_type == ExecuteType.EXECUTE_ALL_UNITS:
        order.trade_all_unit(slippage=slippage,slippage_rate=slippage_rate)
        # elif execute_type == ExecuteType.EXECUTE_WITH_MAX_VOLUME:
        #     order.trade_with_current_volume(int(self.trading_volume()), slippage)
        # else:
        #     return
        execution_record: pd.Series = order.execution_res
        # calculate margin requirement
        # margin_requirement = 0.0
        margin_requirement = self.get_initial_margin(order.long_short) * execution_record[Util.TRADE_UNIT]
        if self.fee_per_unit is None:
            # 百分比手续费
            transaction_fee = execution_record[Util.TRADE_PRICE] * self.fee_rate * execution_record[
                Util.TRADE_UNIT] * self._multiplier
        else:
            # 每手手续费
            transaction_fee = self.fee_per_unit * execution_record[Util.TRADE_UNIT]
        execution_record[Util.TRANSACTION_COST] += transaction_fee
        transaction_fee_add_to_price = transaction_fee / (execution_record[Util.TRADE_UNIT] * self._multiplier)
        execution_record[Util.TRADE_PRICE] += execution_record[
                                                  Util.TRADE_LONG_SHORT].value * transaction_fee_add_to_price
        position_size = order.long_short.value * execution_record[Util.TRADE_PRICE] * execution_record[
            Util.TRADE_UNIT] * self._multiplier
        execution_record[
            Util.TRADE_BOOK_VALUE] = position_size  # 头寸规模（含多空符号），例如，空一手豆粕（3000点，乘数10）得到头寸规模为-30000，而建仓时点头寸市值为0。
        execution_record[Util.TRADE_MARGIN_CAPITAL] = margin_requirement
        # execution_record[
        #     Util.TRADE_MARKET_VALUE] = position_size  # Init value of a future trade is ZERO, except for transaction cost.
        return execution_record

    """ 用于计算杠杆率 ：基础证券交易不包含保证金current value为当前价格 """

    def get_current_value(self, long_short):
        if long_short == LongShort.LONG:
            return self.mktprice_close()
        else:
            return 0.0

    def is_margin_trade(self, long_short):
        if long_short == LongShort.LONG:
            return False
        else:
            return True # 包含融券交易

    def is_mtm(self):
        return False

