import pandas as pd
from typing import Union
import datetime
from back_test.model.constant import FrequentType, Util,LongShort
from back_test.model.base_product import BaseProduct


class BaseFuture(BaseProduct):
    """
    BaseFuture: For Independent Future.
    """

    def __init__(self, df_data: pd.DataFrame, df_daily_data: pd.DataFrame = None,
                 frequency: FrequentType = FrequentType.DAILY):
        super().__init__(df_data, df_daily_data, frequency)
        self._multiplier = Util.DICT_CONTRACT_MULTIPLIER[self.name_code()]

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
        return self.current_state[Util.DT_MATURITY]

    def multiplier(self) -> Union[int,None]:
        return self._multiplier

    def is_margin_trade(self, long_short):
        return True

    def is_mtm(self):
        return True

    def is_core(self) -> Union[bool,None]:
        core_months = Util.DICT_FUTURE_CORE_CONTRACT[self.name_code()]
        if core_months == Util.STR_ALL:
            return True
        else:
            month = int(self.contract_month()[-2:])
            if month in core_months:
                return True
            else:
                return False

