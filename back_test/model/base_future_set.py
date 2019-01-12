import datetime
from collections import deque
from typing import Dict, List, Union
import pandas as pd
from back_test.model.abstract_base_product_set import AbstractBaseProductSet
from back_test.model.base_future import BaseFuture
from back_test.model.base_option import BaseOption
from back_test.model.constant import FrequentType, Util


class BaseFutureSet(AbstractBaseProductSet):
    """
    Feature:

    To Collect BktOption Set
    To Calculate Vol Surface and Metrics
    To Manage Back Test State of all BktOption Objects
    """

    def __init__(self, df_data: pd.DataFrame,
                 df_daily_data: pd.DataFrame = None,
                 df_underlying: pd.DataFrame = None,
                 frequency: FrequentType = FrequentType.DAILY):
        super().__init__()
        self._name_code = df_data.loc[0, Util.ID_INSTRUMENT].split('_')[0].lower()
        self._multiplier = Util.DICT_CONTRACT_MULTIPLIER[self._name_code]
        self.df_data = df_data
        if frequency in Util.LOW_FREQUENT:
            self.df_daily_data = df_data
        else:
            self.df_daily_data = df_daily_data
        self.df_underlying = df_underlying  # df_underlying should have the same frequency with df_data.
        self.frequency: FrequentType = frequency
        self.future_dict: Dict[datetime.date, List(BaseOption)] = {}
        self.future_dict_backup: Dict[datetime.date, List(BaseOption)] = {}
        self.size: int = 0
        self.eval_date: datetime.date = None
        self.eval_datetime: datetime.datetime = None
        self.date_list: List[datetime.date] = None
        self.datetime_list: List[datetime.datetime] = None
        self.current_index = -1
        self.eligible_futures = deque()
        self.eligible_maturities: List(datetime.date) = None  # To be fulled in NEXT() method

    def init(self) -> None:
        self._generate_required_columns_if_missing()
        self._pre_process()
        self.next()

    def _generate_required_columns_if_missing(self) -> None:
        required_column_list = Util.FUTURE_COLUMN_LIST
        columns = self.df_data.columns
        for column in required_column_list:
            if column not in columns:
                self.df_data[column] = None

    def _pre_process(self) -> None:
        if self.frequency in Util.LOW_FREQUENT:
            self.date_list = sorted(self.df_data[Util.DT_DATE].unique())
            self.nbr_index = len(self.date_list)
        else:
            mask = self.df_data.apply(Util.filter_invalid_data, axis=1)
            self.df_data = self.df_data[mask].reset_index(drop=True)
            self.date_list = sorted(self.df_data[Util.DT_DATE].unique())
            self.datetime_list = sorted(self.df_data[Util.DT_DATETIME].unique())
            self.nbr_index = len(self.datetime_list)
            if self.df_daily_data is None:
                return
        groups = self.df_data.groupby([Util.ID_INSTRUMENT])
        if self.df_daily_data is not None:
            groups_daily = self.df_daily_data.groupby([Util.ID_INSTRUMENT])
        else:
            groups_daily = None
        for key in groups.groups.keys():
            # manage minute data and daily data.
            df_future = groups.get_group(key).reset_index(drop=True)
            if self.df_daily_data is not None:
                df_future_daily = groups_daily.get_group(key).reset_index(drop=True)
            else:
                df_future_daily = None
            future = BaseFuture(df_future, df_future_daily, frequency=self.frequency)
            future.init()
            l = self.future_dict.get(future.eval_date)
            if l is None:
                l = []
                self.future_dict.update({future.eval_date: l})
            l.append(future)
            self.size += 1
        self.future_dict_backup = self.future_dict.copy()

    def next(self) -> None:
        # Update index and time,
        self.current_index += 1
        if self.frequency in Util.LOW_FREQUENT:
            self.eval_date = self.date_list[self.current_index]
        else:
            self.eval_datetime = pd.to_datetime(self.datetime_list[self.current_index])
            if self.eval_date != self.eval_datetime.date():
                self.eval_date = self.eval_datetime.date()
        # Update existing deque
        size = len(self.eligible_futures)
        eligible_maturities = []
        for i in range(size):
            future = self.eligible_futures.popleft()
            if not future.has_next():
                continue
            future.next()
            if future.is_valid_future(self.eval_date):
                self._add_future(future)
                if future.maturitydt() not in eligible_maturities:
                    eligible_maturities.append(future.maturitydt())
        for future in self.future_dict.pop(self.eval_date, []):
            if future.is_valid_future(self.eval_date):
                self._add_future(future)
                if future.maturitydt() not in eligible_maturities:
                    eligible_maturities.append(future.maturitydt())
        self.eligible_maturities = sorted(eligible_maturities)
        # Check option data quality.
        if self.frequency not in Util.LOW_FREQUENT:
            for future in self.eligible_futures:
                if self.eval_datetime != future.eval_datetime:
                    print("Future datetime does not match, id : {0}, dt_futureset:{1}, dt_future:{2}".format(
                        future.id_instrument(), self.eval_datetime, future.eval_datetime))
        return None

    def go_to(self, dt: datetime.date):
        """
        set current date for option set
        1. construct eligible options at given date.
        2. set all options in eligible options to the given date.
        3. update other related fields
        :param dt:
        :return:
        """
        # raise error if reset to an invalid date,i.e. date less than the minimum or greater than the maximum
        if dt not in self.date_list:
            raise ValueError("invalid date: {} on optionset {}".format(dt, self))
        # Reset option_dict and eligible_options
        self.future_dict = self.future_dict_backup.copy()
        self.eligible_futures = deque()
        eligible_maturities = set()
        # Loop over option_dict_backup to generate eligible_options
        for date in self.date_list:
            if date > dt:
                break
            for option in self.future_dict_backup.get(date, []):
                if not option.is_valid_option(): continue
                if option.last_date() < dt:
                    continue
                option.go_to(dt)
                eligible_maturities.add(option.maturitydt())
                self.eligible_futures.append(option)
        self.eligible_maturities = sorted(eligible_maturities)
        # Update eval_date and eval_datetime
        if self.frequency in Util.LOW_FREQUENT:
            self.current_index = next((index for index, val in enumerate(self.date_list) if val >= dt), -1)
            self.eval_date = self.date_list[self.current_index]
        else:
            self.current_index = next((index for index, val in enumerate(self.datetime_list) if val >= dt), -1)
            self.eval_datetime = self.datetime_list[self.current_index]
            self.eval_date = self.eval_datetime.date()

    def __repr__(self) -> str:
        return 'BaseFutureSet(evalDate:{0}, totalSize: {1})' \
            .format(self.eval_date, self.size)

    def get_current_state(self) -> pd.DataFrame:
        df_current_state = self.df_data[self.df_data[Util.DT_DATE] == self.eval_date].reset_index(drop=True)
        return df_current_state

    def _add_future(self, future: BaseFuture) -> None:
        self.eligible_futures.append(future)

    def has_next(self) -> bool:
        return self.current_index < self.nbr_index - 1

    def has_next_minute(self) -> bool:
        if self.frequency in Util.LOW_FREQUENT or self.current_index == self.nbr_index:
            return False
        else:
            next_datetime = pd.to_datetime(self.datetime_list[self.current_index + 1])
            if self.eval_date == next_datetime.date():
                return True
            else:
                return False

    def get_basefuture_by_id(self,id):
        for future in self.eligible_futures:
            if future.id_instrument() == id:
                return future

    # 到期日与月份的对应关系表
    def update_contract_month_maturity_table(self):
        self.df_maturity_and_contract_months = self.df_daily_data.drop_duplicates(Util.NAME_CONTRACT_MONTH) \
            .sort_values(by=Util.NAME_CONTRACT_MONTH).reset_index(drop=True) \
            [[Util.NAME_CONTRACT_MONTH, Util.DT_MATURITY]]

    def get_maturities_list(self) -> List[datetime.date]:
        list_maturities = []
        for future in self.eligible_futures:
            maturitydt = future.maturitydt()
            if maturitydt not in list_maturities: list_maturities.append(maturitydt)
        list_maturities = sorted(list_maturities)
        return list_maturities

    def select_maturity_date(self, nbr_maturity, min_holding: int = 0):
        maturities = self.get_maturities_list()
        idx_start = 0
        if (maturities[idx_start] - self.eval_date).days <= min_holding:
            idx_start += 1
        idx_maturity = idx_start + nbr_maturity
        if idx_maturity > len(maturities) - 1:
            return
        else:
            return maturities[idx_maturity]

    # TODO: MOVE TO CONSTENT
    def select_higher_volume(self, futures: List[BaseFuture]) -> Union[None,BaseFuture]:
        volume0 = 0.0
        res = None
        if futures is None: return
        for future in futures:
            volume = future.trading_volume()
            if volume >= volume0: res = future
            volume0 = volume
        return res

