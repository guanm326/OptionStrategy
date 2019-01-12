import pandas as pd
from typing import Union
import datetime
from back_test.model.constant import FrequentType, Util,LongShort,ExecuteType
from back_test.model.base_product import BaseProduct
from back_test.model.trade import Order


class BaseFuture(BaseProduct):
    """
    BaseFuture: For Independent Future.
    """

    def __init__(self, df_data: pd.DataFrame, df_daily_data: pd.DataFrame = None,
                 frequency: FrequentType = FrequentType.DAILY):
        super().__init__(df_data, df_daily_data, frequency)
        self._multiplier = Util.DICT_CONTRACT_MULTIPLIER[self.name_code()]
        self.fee_rate = Util.DICT_TRANSACTION_FEE_RATE[self.name_code()]
        self.fee_per_unit = Util.DICT_TRANSACTION_FEE[self.name_code()]

    def __repr__(self) -> str:
        return 'BaseInstrument(id_instrument: {0},eval_date: {1},frequency: {2})' \
            .format(self.id_instrument(), self.eval_date, self.frequency)

    def is_valid_future(self, eval_date) -> bool:
        return True


    """ getters """

    def contract_month(self) -> Union[str, None]:
        return self.current_state[Util.NAME_CONTRACT_MONTH]

    def get_fund_required(self, long_short: LongShort) -> float:
        return self.get_initial_margin(long_short)

    def get_initial_margin(self,long_short:LongShort) -> Union[float,None]:
        return self.get_maintain_margin(long_short)

    def get_maintain_margin(self,long_short:LongShort) -> Union[float,None]:
        margin_rate = Util.DICT_FUTURE_MARGIN_RATE[self.name_code()]
        pre_settle_price = self.mktprice_last_settlement()
        margin = pre_settle_price * margin_rate * self._multiplier
        return margin

    def maturitydt(self) -> Union[datetime.date,None]:
        if self.current_state[Util.DT_MATURITY] != Util.NAN_VALUE:
            maturity = self.current_state[Util.DT_MATURITY]
        else:
            maturity = self.df_daily_data.loc[self.nbr_index - 1, Util.DT_DATE]
        return maturity

    def multiplier(self) -> Union[int,None]:
        return self._multiplier

    def is_margin_trade(self, long_short):
        return True

    def is_mtm(self):
        return True

    def execute_order(self, order: Order, slippage=0,slippage_rate=0.0, execute_type: ExecuteType = ExecuteType.EXECUTE_ALL_UNITS):
        if order is None or order.trade_unit == 0: return
        # if execute_type == ExecuteType.EXECUTE_ALL_UNITS:
        order.trade_all_unit(slippage=slippage,slippage_rate=slippage_rate)
        # elif execute_type == ExecuteType.EXECUTE_WITH_MAX_VOLUME:
        #     order.trade_with_current_volume(int(self.trading_volume()), slippage,slippage_rate)
        # else:
        #     return
        execution_record: pd.Series = order.execution_res
        # calculate margin requirement
        margin_requirement = self.get_initial_margin(order.long_short) * execution_record[Util.TRADE_UNIT]
        if self.fee_per_unit is None:
            # 百分比手续费
            transaction_fee = execution_record[Util.TRADE_PRICE] * self.fee_rate * execution_record[
                Util.TRADE_UNIT] * self._multiplier
        else:
            # 每手手续费`
            transaction_fee = self.fee_per_unit * execution_record[Util.TRADE_UNIT]
        execution_record[Util.TRANSACTION_COST] += transaction_fee
        transaction_fee_add_to_price = transaction_fee / (execution_record[Util.TRADE_UNIT] * self._multiplier)
        execution_record[Util.TRADE_PRICE] += execution_record[
                                                  Util.TRADE_LONG_SHORT].value * transaction_fee_add_to_price
        position_size = order.long_short.value * execution_record[Util.TRADE_PRICE] * execution_record[
            Util.TRADE_UNIT] * self._multiplier
        execution_record[Util.TRADE_BOOK_VALUE] = position_size  # 头寸规模（含多空符号），例如，空一手豆粕（3000点，乘数10）得到头寸规模为-30000，而建仓时点头寸市值为0。
        execution_record[Util.TRADE_MARGIN_CAPITAL] = margin_requirement
        execution_record[Util.TRADE_MARKET_VALUE] = 0.0  # 建仓时点头寸市值为0
        return execution_record

