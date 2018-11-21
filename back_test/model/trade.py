import datetime
import uuid
from enum import Enum
from typing import Union

import pandas as pd

from back_test.model.constant import LongShort, Util


class OrderStatus(Enum):
    INITIAL = 0
    PROCESSING = 1
    COMPLETE = 2


class Trade():
    def __init__(self):
        self.pending_orders = []


    def add_pending_order(self, order):
        if order.status == OrderStatus.PROCESSING:
            self.pending_orders.append(order)
            order.trade_unit = order.pending_unit
            order.trade_price = None
            order.time_signal = None


class Order(object):
    def __init__(self,
                 dt_trade: datetime.date,
                 id_instrument: str,
                 trade_unit: Union[int, None],
                 trade_price: Union[float, None],
                 time_signal: Union[datetime.datetime, None],
                 long_short):
        super().__init__()
        if trade_unit < 0:
            print('Order has negative unit, reset to positive.')
        self._trade_unit = abs(trade_unit)
        self._dt_trade: datetime = dt_trade
        self._id_instrument = id_instrument
        self._long_short = long_short
        self._trade_price = trade_price
        self._time_signal = time_signal
        self._status = OrderStatus.INITIAL
        self._pending_unit = 0
        self._uuid = uuid.uuid4()
        self.execution_res = None

    @property
    def long_short(self) -> LongShort:
        return self._long_short

    @property
    def dt_trade(self) -> datetime.date:
        return self._dt_trade

    @dt_trade.setter
    def dt_trade(self, dt_trade: datetime.date) -> None:
        self._dt_trade = dt_trade

    @property
    def id_instrument(self):
        return self._id_instrument

    @id_instrument.setter
    def id_instrument(self, id_instrument: str) -> None:
        self._id_instrument = id_instrument

    @property
    def trade_unit(self) -> int:
        return self._trade_unit

    # @trade_unit.setter
    # def trade_unit(self, trade_unit: int) -> None:
    #     self._trade_unit = trade_unit

    @property
    def trade_price(self) -> float:
        return self._trade_price

    @trade_price.setter
    def trade_price(self, trade_price: int) -> None:
        self._trade_price = trade_price

    @property
    def time_signal(self) -> datetime.datetime:
        return self._time_signal

    @time_signal.setter
    def time_signal(self, time_signale: datetime.datetime) -> None:
        self._time_signal = time_signale

    @property
    def status(self) -> OrderStatus:
        return self._status

    @status.setter
    def status(self, status: OrderStatus) -> None:
        self._status = status

    @property
    def pending_unit(self) -> int:
        return self._pending_unit

    @pending_unit.setter
    def pending_unit(self, unit: int) -> None:
        self._pending_unit = unit

    @property
    def uuid(self) -> uuid:
        return self._uuid

    def trade_all_unit(self, slippage, slippage_rate) -> None:
        executed_units = self.trade_unit
        name_code = self.id_instrument.split("_")[0]
        # buy at slippage tick size higher and sell lower.
        if slippage_rate > 0:
            executed_price = self.trade_price + self.long_short.value * slippage_rate * self.trade_price
            slippage_cost = 0.0  # 滑点费用暂不在交易手续费中统计。
        elif slippage > 0:
            executed_price = self.trade_price + self.long_short.value * slippage * Util.DICT_TICK_SIZE[name_code]
            # slippage_cost = slippage * Util.DICT_TICK_SIZE[name_code] * executed_units
            slippage_cost = 0.0  # 滑点费用暂不在交易手续费中统计。
        else:
            executed_price = self.trade_price
            slippage_cost = 0.0
        # transaction cost will be added in base_product
        excution_res = pd.Series(
            {
                Util.UUID: uuid.uuid4(),
                Util.DT_TRADE: self.dt_trade,
                Util.ID_INSTRUMENT: self.id_instrument,
                Util.TRADE_LONG_SHORT: self.long_short,
                Util.TRADE_UNIT: executed_units,
                Util.TRADE_PRICE: executed_price,
                # Util.TRADE_TYPE: self.trade_type,
                Util.TIME_SIGNAL: self.time_signal,
                Util.TRANSACTION_COST: slippage_cost
            }
        )

        self.execution_res = excution_res


    # def trade_with_current_volume(self,
    #                               max_volume: int,
    #                               slippage: int = 0) -> None:
    #     if self.trade_unit < max_volume:
    #         executed_units = self.trade_unit
    #         self.status = OrderStatus.COMPLETE
    #         self.pending_unit = 0.0
    #     else:
    #         executed_units = max_volume
    #         self.status = OrderStatus.PROCESSING
    #         self.pending_unit = self.trade_unit - max_volume
    #         # self.pending_order = Order(self.dt_trade,self.id_instrument,self.trade_type,
    #         #                            self.pending_unit,None,None)
    #
    #     name_code = self.id_instrument.split("_")[0]
    #     # buy at slippage tick size higher and sell lower.
    #     executed_price = self.trade_price + self.long_short.value * slippage * Util.DICT_TICK_SIZE[name_code]
    #     # transaction cost will be added in base_product
    #     slippage_cost = slippage * Util.DICT_TICK_SIZE[name_code] * executed_units
    #     excution_res = pd.Series(
    #         {
    #             Util.UUID: uuid.uuid4(),
    #             Util.DT_TRADE: self.dt_trade,
    #             Util.ID_INSTRUMENT: self.id_instrument,
    #             Util.TRADE_LONG_SHORT: self.long_short,
    #             Util.TRADE_UNIT: executed_units,
    #             Util.TRADE_PRICE: executed_price,
    #             # Util.TRADE_TYPE: self.trade_type,
    #             Util.TIME_SIGNAL: self.time_signal,
    #             Util.TRANSACTION_COST: slippage_cost
    #         }
    #     )
    #
    #     self.execution_res = excution_res
