import datetime
from collections import deque
from typing import Dict, List, Tuple
import pandas as pd
import numpy as np
import math
from back_test.model.abstract_base_product_set import AbstractBaseProductSet
from back_test.model.base_future import BaseFuture
from back_test.model.base_option import BaseOption
from back_test.model.constant import FrequentType, Util, OptionFilter, OptionType, OptionUtil, Option50ETF, \
    OptionExerciseType,CdPriceType
from PricingLibrary.EngineQuantlib import QlBinomial, QlBlackFormula, QlBAW
from PricingLibrary.BinomialModel import BinomialTree


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
                 frequency: FrequentType = FrequentType.DAILY,
                 rf: float = 0.03):
        super().__init__()
        self._name_code = df_data.loc[0, Util.ID_INSTRUMENT].split('_')[0]
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
        self.rf: float = rf
        self.size: int = 0
        self.eval_date: datetime.date = None
        self.eval_datetime: datetime.datetime = None
        self.date_list: List[datetime.date] = None
        self.datetime_list: List[datetime.datetime] = None
        self.current_index = -1
        self.eligible_futures = deque()
        # self.update_contract_month_maturity_table()  # _generate_required_columns_if_missing的时候就要用到
        self.eligible_maturities: List(datetime.date) = None  # To be fulled in NEXT() method
        # self.OptionUtilClass = OptionUtil.get_option_util_class(self._name_code)
        if self._name_code in ['m', 'sr']:
            self.exercise_type = OptionExerciseType.AMERICAN
        else:
            self.exercise_type = OptionExerciseType.EUROPEAN

    def init(self) -> None:
        # self._generate_required_columns_if_missing()  # 补充行权价等关键信息（high frequency data就可能没有）
        self.pre_process()
        self.next()

    # def _generate_required_columns_if_missing(self) -> None:
    #     required_column_list = Util.OPTION_COLUMN_LIST
    #     columns = self.df_data.columns
    #     for column in required_column_list:
    #         if column not in columns:
    #             self.df_data[column] = None
        # # DT_MATURITY -> datetime.date : 通过contract month查找
        # if self.df_data.loc[0, Util.DT_MATURITY] is None or pd.isnull(self.df_data.loc[0, Util.DT_MATURITY]):
        #     # self.df_data[Util.DT_MATURITY] = self.df_data.apply(OptionFilter.fun_option_maturity, axis=1)
        #     self.df_data[Util.DT_MATURITY] = self.df_data.apply(
        #         lambda x: OptionFilter.dict_maturities[x[Util.ID_UNDERLYING]] if pd.isnull(x[Util.DT_MATURITY]) else x[
        #             Util.DT_MATURITY], axis=1)
        # # STRIKE -> float
        # if self.df_data.loc[0, Util.AMT_STRIKE] is None or pd.isnull(self.df_data.loc[0, Util.AMT_STRIKE]):
        #     self.df_data[Util.AMT_STRIKE] = self.df_data.apply(
        #         lambda x: float(x[Util.ID_INSTRUMENT].split('_')[3]) if pd.isnull(x[Util.AMT_STRIKE]) else x[
        #             Util.AMT_STRIKE], axis=1)
        # # NAME_CONTRACT_MONTH -> String
        # if self.df_data.loc[0, Util.NAME_CONTRACT_MONTH] is None or pd.isnull(
        #         self.df_data.loc[0, Util.NAME_CONTRACT_MONTH]):
        #     self.df_data[Util.NAME_CONTRACT_MONTH] = self.df_data.apply(
        #         lambda x: float(x[Util.ID_INSTRUMENT].split('_')[1]) if pd.isnull(x[Util.NAME_CONTRACT_MONTH]) else x[
        #             Util.NAME_CONTRACT_MONTH], axis=1)
        # # OPTION_TYPE -> String
        # if self.df_data.loc[0, Util.CD_OPTION_TYPE] is None or pd.isnull(self.df_data.loc[0, Util.CD_OPTION_TYPE]):
        #     self.df_data[Util.CD_OPTION_TYPE] = self.df_data.apply(OptionFilter.fun_option_type_split, axis=1)
        # # MULTIPLIER -> int: 50etf期权的multiplier跟id_instrument有关，需补充该列实际值。（商品期权multiplier是固定的）
        # if self._name_code == Util.STR_50ETF:
        #     if self.df_data.loc[0, Util.NBR_MULTIPLIER] is None or np.isnan(self.df_data.loc[0, Util.NBR_MULTIPLIER]):
        #         self.df_data = self.df_data.drop(Util.NBR_MULTIPLIER, axis=1).join(
        #             self.get_id_multiplier_table().set_index(Util.ID_INSTRUMENT),
        #             how='left', on=Util.ID_INSTRUMENT
        #         )
        # # ID_UNDERLYING : 通过name code 与 contract month补充
        # if self.df_data.loc[0, Util.ID_UNDERLYING] is None or pd.isnull(self.df_data.loc[0, Util.ID_UNDERLYING]):
        #     if self._name_code == Util.STR_50ETF:
        #         self.df_data.loc[:, Util.ID_UNDERLYING] = Util.STR_INDEX_50ETF
        #     else:
        #         self.df_data.loc[:, Util.ID_UNDERLYING] = self._name_code + self.df_data.loc[:,
        #                                                                     Util.NAME_CONTRACT_MONTH]

    def get_id_multiplier_table(self):
        df_id_multiplier = self.df_daily_data.drop_duplicates(
            Util.ID_INSTRUMENT)[[Util.ID_INSTRUMENT, Util.NBR_MULTIPLIER]]
        return df_id_multiplier

    def pre_process(self) -> None:

        if self.frequency in Util.LOW_FREQUENT:
            self.date_list = sorted(self.df_data[Util.DT_DATE].unique())
            self.nbr_index = len(self.date_list)
        else:
            mask = self.df_data.apply(Util.filter_invalid_data, axis=1)
            # TODO:
            # 高频数据预处理：根据日频数据的id_instrument与dt_datetime，
            # 对高频数据（df_data）进行补充，缺失数据用前值代替，成交量填0.
            self.df_data = self.df_data[mask].reset_index(drop=True)
            self.date_list = sorted(self.df_data[Util.DT_DATE].unique())
            self.datetime_list = sorted(self.df_data[Util.DT_DATETIME].unique())
            self.nbr_index = len(self.datetime_list)
            if self.df_daily_data is None:
                return
        # self.df_data[Util.AMT_APPLICABLE_STRIKE] = self.df_data.apply(self.OptionUtilClass.fun_applicable_strike,
        #                                                               axis=1)
        # self.df_data = self.df_data.rename(columns={Util.NBR_MULTIPLIER:Util.NBR_MULTIPLIER_AFTER_ADJ})
        # self.df_data[Util.NBR_MULTIPLIER] = self.df_data.apply(self.OptionUtilClass.fun_applicable_multiplier,axis=1)
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
            future = BaseFuture(df_future, df_future_daily, frequency=self.frequency,
                                rf=self.rf)
            future.init()
            l = self.option_dict.get(future.eval_date)
            if l is None:
                l = []
                self.option_dict.update({future.eval_date: l})
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
            if future.is_valid_option(self.eval_date):
                self.add_option(future)
                if future.maturitydt() not in eligible_maturities:
                    eligible_maturities.append(future.maturitydt())
        for option in self.option_dict.pop(self.eval_date, []):
            if option.is_valid_option(self.eval_date):
                self.add_option(option)
                if option.maturitydt() not in eligible_maturities:
                    eligible_maturities.append(option.maturitydt())
        self.eligible_maturities = sorted(eligible_maturities)
        # Check option data quality.
        if self.frequency not in Util.LOW_FREQUENT:
            for option in self.eligible_futures:
                if self.eval_datetime != option.eval_datetime:
                    print("Option datetime does not match, id : {0}, dt_optionset:{1}, dt_option:{2}".format(
                        option.id_instrument(), self.eval_datetime, option.eval_datetime))
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
        self.option_dict = self.option_dict_backup.copy()
        self.eligible_options = deque()
        eligible_maturities = set()
        # Loop over option_dict_backup to generate eligible_options
        for date in self.date_list:
            if date > dt:
                break
            for option in self.option_dict_backup.get(date, []):
                if not option.is_valid_option(): continue
                if option.last_date() < dt:
                    continue
                option.go_to(dt)
                eligible_maturities.add(option.maturitydt())
                self.eligible_options.append(option)
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
        return 'BaseOptionSet(evalDate:{0}, totalSize: {1})' \
            .format(self.eval_date, self.size)

    def add_option(self, option: BaseOption) -> None:
        self.eligible_options.append(option)

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

    def get_baseoption_by_id(self,id):
        for option in self.eligible_options:
            if option.id_instrument() == id:
                return option


    def get_current_state(self) -> pd.DataFrame:
        df_current_state = self.df_data[self.df_data[Util.DT_DATE] == self.eval_date].reset_index(drop=True)
        return df_current_state

    # 期权到期日与期权和月份的对应关系表
    def update_contract_month_maturity_table(self):
        self.df_maturity_and_contract_months = self.df_daily_data.drop_duplicates(Util.NAME_CONTRACT_MONTH) \
            .sort_values(by=Util.NAME_CONTRACT_MONTH).reset_index(drop=True) \
            [[Util.NAME_CONTRACT_MONTH, Util.DT_MATURITY]]

    def get_maturities_list(self) -> List[datetime.date]:
        list_maturities = []
        for option in self.eligible_options:
            maturitydt = option.maturitydt()
            if maturitydt not in list_maturities: list_maturities.append(maturitydt)
        list_maturities = sorted(list_maturities)
        return list_maturities

    # get Dictionary <contract month, List[option]>
    def get_dict_options_by_contract_months(self):
        dic = {}
        for option in self.eligible_options:
            if option.contract_month() in dic.keys():
                dic[option.contract_month()].append(option)
            else:
                dic.update({option.contract_month(): [option]})
        return dic

    # get Dictionary <maturitydt, List[option]>
    def get_dict_options_by_maturities(self):
        dic = {}
        for option in self.eligible_options:
            if option.maturitydt() in dic.keys():
                dic[option.maturitydt()].append(option)
            else:
                dic.update({option.maturitydt(): [option]})
        return dic

    # 根据到期日或合约月份查找标的价格，需重新计算（暂未用到）
    def get_underlying_close(self, contract_month=None, maturitydt=None):
        # 对于商品期权，underlying要从对应的月份合约中找。
        if self._name_code == Util.STR_50ETF:
            spot = self.eligible_options[0].underlying_close()
        else:
            if contract_month is not None:
                option_list = self.get_dict_options_by_contract_months()[contract_month]
                spot = option_list[0].underlying_close()
            elif maturitydt is not None:
                option_list = self.get_dict_options_by_maturities()[maturitydt]
                spot = option_list[0].underlying_close()
            else:
                print('No contract month or maturity specified for commodity option.')
                maturitydt = sorted(self.get_dict_options_by_maturities().keys())[0]
                option_list = self.get_dict_options_by_maturities()[maturitydt]
                spot = option_list[0].underlying_close()
        return spot

    def get_T_quotes(self, dt_maturity, cd_option_price):
        df_current = self.get_current_state()
        df_mdt = df_current[df_current[Util.DT_MATURITY] == dt_maturity].reset_index(drop=True)
        if cd_option_price == Util.CD_CLOSE_VOLUME_WEIGHTED:
            df_call = df_mdt[df_mdt[Util.CD_OPTION_TYPE] == Util.STR_CALL].rename(
                columns={Util.AMT_CLOSE_VOLUME_WEIGHTED: Util.AMT_CALL_QUOTE,
                         Util.AMT_TRADING_VOLUME: Util.AMT_TRADING_VOLUME_CALL,
                         Util.ID_INSTRUMENT: Util.ID_CALL})
            df_put = df_mdt[df_mdt[Util.CD_OPTION_TYPE] == Util.STR_PUT].rename(
                columns={Util.AMT_CLOSE_VOLUME_WEIGHTED: Util.AMT_PUT_QUOTE,
                         Util.AMT_TRADING_VOLUME: Util.AMT_TRADING_VOLUME_PUT,
                         Util.ID_INSTRUMENT: Util.ID_PUT})
        else:
            df_call = df_mdt[df_mdt[Util.CD_OPTION_TYPE] == Util.STR_CALL].rename(
                columns={Util.AMT_CLOSE: Util.AMT_CALL_QUOTE, Util.AMT_TRADING_VOLUME: Util.AMT_TRADING_VOLUME_CALL,
                         Util.ID_INSTRUMENT: Util.ID_CALL})
            df_put = df_mdt[df_mdt[Util.CD_OPTION_TYPE] == Util.STR_PUT].rename(
                columns={Util.AMT_CLOSE: Util.AMT_PUT_QUOTE, Util.AMT_TRADING_VOLUME: Util.AMT_TRADING_VOLUME_PUT,
                         Util.ID_INSTRUMENT: Util.ID_PUT})

        df = pd.merge(df_call[[Util.ID_CALL,Util.NAME_CONTRACT_MONTH, Util.DT_DATE, Util.AMT_CALL_QUOTE, Util.AMT_APPLICABLE_STRIKE,
                               Util.AMT_STRIKE,
                               Util.DT_MATURITY, Util.AMT_UNDERLYING_CLOSE, Util.AMT_TRADING_VOLUME_CALL]],
                      df_put[[Util.ID_PUT,Util.AMT_PUT_QUOTE, Util.AMT_APPLICABLE_STRIKE, Util.AMT_TRADING_VOLUME_PUT]],
                      how='inner', on=Util.AMT_APPLICABLE_STRIKE)
        df[Util.AMT_TRADING_VOLUME] = df[Util.AMT_TRADING_VOLUME_CALL] + df[Util.AMT_TRADING_VOLUME_PUT]
        ttm = ((dt_maturity - self.eval_date).total_seconds() / 60.0) / (365.0 * 1440)
        df['amt_ttm'] = ttm
        return df

    # 根据行权价在OTM IMPLIED CURVE上选择对应的波动率
    def get_iv_by_otm_iv_curve(self, dt_maturity, strike):
        df = self.get_otm_implied_vol_curve(dt_maturity)
        iv = df[df[Util.AMT_APPLICABLE_STRIKE] == strike][Util.PCT_IV_OTM_BY_HTBR].values[0]
        return iv

    # 平值隐含波动率根据平价公式与HTB RATE调整，认沽与认购隐含波动率相同。
    def get_atm_iv_by_htbr(self, dt_maturity, cd_option_price=Util.CD_CLOSE):
        t_qupte = self.get_T_quotes(dt_maturity, cd_option_price)
        t_qupte.loc[:, 'diff'] = abs(
            t_qupte.loc[:, Util.AMT_APPLICABLE_STRIKE] - t_qupte.loc[:, Util.AMT_UNDERLYING_CLOSE])
        atm_series = t_qupte.loc[t_qupte['diff'].idxmin()]
        # atm_strike = atm_series[Util.AMT_STRIKE]
        htb_r = self.fun_htb_rate(atm_series, self.rf)
        iv = self.fun_htb_rate_adjusted_iv(atm_series, OptionType.CALL, htb_r)
        return iv

    # 隐含波动率曲线（OTM）
    def get_otm_implied_vol_curve(self, dt_maturity, cd_option_price=Util.CD_CLOSE):
        t_qupte = self.get_T_quotes(dt_maturity, cd_option_price)
        t_qupte.loc[:, 'diff'] = abs(
            t_qupte.loc[:, Util.AMT_APPLICABLE_STRIKE] - t_qupte.loc[:, Util.AMT_UNDERLYING_CLOSE])
        atm_series = t_qupte.loc[t_qupte['diff'].idxmin()]
        htb_r = self.fun_htb_rate(atm_series, self.rf)
        t_qupte.loc[:, Util.AMT_HTB_RATE] = htb_r
        t_qupte[Util.PCT_IV_CALL_BY_HTBR] = t_qupte.apply(
            lambda x: self.fun_htb_rate_adjusted_iv(x, OptionType.CALL, htb_r), axis=1)
        t_qupte[Util.PCT_IV_PUT_BY_HTBR] = t_qupte.apply(
            lambda x: self.fun_htb_rate_adjusted_iv(x, OptionType.PUT, htb_r), axis=1)
        t_qupte[Util.PCT_IV_OTM_BY_HTBR] = t_qupte.apply(self.fun_otm_iv, axis=1)
        return t_qupte[
            [Util.AMT_APPLICABLE_STRIKE, Util.AMT_UNDERLYING_CLOSE, Util.DT_MATURITY, Util.PCT_IV_OTM_BY_HTBR,
             Util.AMT_HTB_RATE]]

    # 成交量加权均价隐含波动率（商品期权）
    def get_volume_weighted_iv(self, dt_maturity, min_iv=0.05, max_iv=1.5):
        df = self.get_implied_vol_curves(dt_maturity)
        df = df[(df[Util.PCT_IV_CALL] >= min_iv) & (df[Util.PCT_IV_CALL] <= max_iv) &
                (df[Util.PCT_IV_PUT] >= min_iv) & (df[Util.PCT_IV_PUT] <= max_iv)]
        if len(df) == 0:
            return None
        iv_vw = (sum(df[Util.PCT_IV_CALL] * df[Util.AMT_TRADING_VOLUME_CALL]) +
                 sum(df[Util.PCT_IV_PUT] * df[Util.AMT_TRADING_VOLUME_PUT])) \
                / sum(df[Util.AMT_TRADING_VOLUME_CALL] + df[Util.AMT_TRADING_VOLUME_PUT])
        return iv_vw

    # 成交量加权均价隐含波动率HTB Rate调整（商品期权）
    def get_volume_weighted_iv_htbr(self, dt_maturity, min_iv=0.05, max_iv=1.5):
        df = self.get_implied_vol_curves_htbr(dt_maturity)
        df = df[(df[Util.PCT_IV_CALL_BY_HTBR] >= min_iv) & (df[Util.PCT_IV_CALL_BY_HTBR] <= max_iv) &
                (df[Util.PCT_IV_PUT_BY_HTBR] >= min_iv) & (df[Util.PCT_IV_PUT_BY_HTBR] <= max_iv)]
        iv_vw = (sum(df[Util.PCT_IV_CALL_BY_HTBR] * df[Util.AMT_TRADING_VOLUME_CALL]) +
                 sum(df[Util.PCT_IV_PUT_BY_HTBR] * df[Util.AMT_TRADING_VOLUME_PUT])) \
                / sum(df[Util.AMT_TRADING_VOLUME_CALL] + df[Util.AMT_TRADING_VOLUME_PUT])
        return iv_vw

    def get_implied_vol_curves(self, dt_maturity, cd_option_price=Util.CD_CLOSE):
        t_qupte = self.get_T_quotes(dt_maturity, cd_option_price)
        t_qupte[Util.PCT_IV_CALL] = t_qupte.apply(lambda x: self.fun_iv(x, OptionType.CALL), axis=1)
        t_qupte[Util.PCT_IV_PUT] = t_qupte.apply(lambda x: self.fun_iv(x, OptionType.PUT), axis=1)
        return t_qupte[[Util.AMT_APPLICABLE_STRIKE, Util.AMT_UNDERLYING_CLOSE, Util.DT_MATURITY,
                        Util.AMT_CALL_QUOTE, Util.PCT_IV_CALL, Util.AMT_TRADING_VOLUME_CALL,
                        Util.AMT_PUT_QUOTE, Util.PCT_IV_PUT, Util.AMT_TRADING_VOLUME_PUT]]

    def get_implied_vol_curves_htbr(self, dt_maturity, cd_option_price=Util.CD_CLOSE):
        t_qupte = self.get_T_quotes(dt_maturity, cd_option_price)
        t_qupte.loc[:, 'diff'] = abs(
            t_qupte.loc[:, Util.AMT_APPLICABLE_STRIKE] - t_qupte.loc[:, Util.AMT_UNDERLYING_CLOSE])
        atm_series = t_qupte.loc[t_qupte['diff'].idxmin()]
        htb_r = self.fun_htb_rate(atm_series, self.rf)
        t_qupte.loc[:, Util.AMT_HTB_RATE] = htb_r
        t_qupte[Util.PCT_IV_CALL_BY_HTBR] = t_qupte.apply(
            lambda x: self.fun_htb_rate_adjusted_iv(x, OptionType.CALL, htb_r), axis=1)
        t_qupte[Util.PCT_IV_PUT_BY_HTBR] = t_qupte.apply(
            lambda x: self.fun_htb_rate_adjusted_iv(x, OptionType.PUT, htb_r), axis=1)
        return t_qupte[[Util.AMT_APPLICABLE_STRIKE, Util.AMT_UNDERLYING_CLOSE, Util.DT_MATURITY, Util.AMT_HTB_RATE,
                        Util.AMT_CALL_QUOTE, Util.PCT_IV_CALL_BY_HTBR, Util.AMT_TRADING_VOLUME_CALL,
                        Util.AMT_PUT_QUOTE, Util.PCT_IV_PUT_BY_HTBR, Util.AMT_TRADING_VOLUME_PUT]]

    def get_call_implied_vol_curve(self, dt_maturity, cd_option_price=Util.CD_CLOSE):
        t_qupte = self.get_T_quotes(dt_maturity, cd_option_price)
        t_qupte[Util.PCT_IV_CALL] = t_qupte.apply(lambda x: self.fun_iv(x, OptionType.CALL), axis=1)
        return t_qupte[[Util.AMT_APPLICABLE_STRIKE, Util.AMT_UNDERLYING_CLOSE,
                        Util.DT_MATURITY, Util.AMT_CALL_QUOTE, Util.PCT_IV_CALL, Util.AMT_TRADING_VOLUME_CALL]]

    def get_put_implied_vol_curve(self, dt_maturity, cd_option_price=Util.CD_CLOSE):
        t_qupte = self.get_T_quotes(dt_maturity, cd_option_price)
        t_qupte[Util.PCT_IV_PUT] = t_qupte.apply(lambda x: self.fun_iv(x, OptionType.PUT), axis=1)
        return t_qupte[[Util.AMT_APPLICABLE_STRIKE, Util.AMT_UNDERLYING_CLOSE,
                        Util.DT_MATURITY, Util.AMT_PUT_QUOTE, Util.PCT_IV_PUT, Util.AMT_TRADING_VOLUME_PUT]]

    def get_call_implied_vol_curve_htbr(self, dt_maturity, cd_option_price=Util.CD_CLOSE):
        t_qupte = self.get_T_quotes(dt_maturity, cd_option_price)
        t_qupte.loc[:, 'diff'] = abs(
            t_qupte.loc[:, Util.AMT_APPLICABLE_STRIKE] - t_qupte.loc[:, Util.AMT_UNDERLYING_CLOSE])
        atm_series = t_qupte.loc[t_qupte['diff'].idxmin()]
        htb_r = self.fun_htb_rate(atm_series, self.rf)
        t_qupte.loc[:, Util.AMT_HTB_RATE] = htb_r
        t_qupte[Util.PCT_IV_CALL_BY_HTBR] = t_qupte.apply(
            lambda x: self.fun_htb_rate_adjusted_iv(x, OptionType.CALL, htb_r), axis=1)
        return t_qupte[[Util.AMT_APPLICABLE_STRIKE, Util.AMT_UNDERLYING_CLOSE, Util.DT_MATURITY,
                        Util.AMT_CALL_QUOTE, Util.PCT_IV_CALL_BY_HTBR, Util.AMT_HTB_RATE, Util.AMT_TRADING_VOLUME_CALL]]

    def get_put_implied_vol_curve_htbr(self, dt_maturity, cd_option_price=Util.CD_CLOSE):
        t_qupte = self.get_T_quotes(dt_maturity, cd_option_price)
        t_qupte.loc[:, 'diff'] = abs(
            t_qupte.loc[:, Util.AMT_APPLICABLE_STRIKE] - t_qupte.loc[:, Util.AMT_UNDERLYING_CLOSE])
        atm_series = t_qupte.loc[t_qupte['diff'].idxmin()]
        htb_r = self.fun_htb_rate(atm_series, self.rf)
        t_qupte.loc[:, Util.AMT_HTB_RATE] = htb_r
        t_qupte[Util.PCT_IV_PUT_BY_HTBR] = t_qupte.apply(
            lambda x: self.fun_htb_rate_adjusted_iv(x, OptionType.PUT, htb_r), axis=1)
        return t_qupte[[Util.AMT_APPLICABLE_STRIKE, Util.AMT_UNDERLYING_CLOSE, Util.DT_MATURITY,
                        Util.AMT_PUT_QUOTE, Util.PCT_IV_PUT_BY_HTBR, Util.AMT_HTB_RATE, Util.AMT_TRADING_VOLUME_PUT]]

    def fun_otm_iv(self, df_series):
        K = df_series[Util.AMT_APPLICABLE_STRIKE]
        S = df_series[Util.AMT_UNDERLYING_CLOSE]
        if K <= S:
            return df_series[Util.PCT_IV_PUT_BY_HTBR]
        else:
            return df_series[Util.PCT_IV_CALL_BY_HTBR]

    def fun_htb_rate_adjusted_iv(self, df_series: pd.DataFrame, option_type: OptionType, htb_r: float):
        ttm = df_series[Util.AMT_TTM]
        K = df_series[Util.AMT_APPLICABLE_STRIKE]
        S = df_series[Util.AMT_UNDERLYING_CLOSE] * math.exp(-htb_r * ttm)
        dt_eval = df_series[Util.DT_DATE]
        dt_maturity = df_series[Util.DT_MATURITY]
        if option_type == OptionType.CALL:
            C = df_series[Util.AMT_CALL_QUOTE]
            if self.exercise_type == OptionExerciseType.EUROPEAN:
                pricing_engine = QlBlackFormula(dt_eval, dt_maturity, OptionType.CALL, S, K, self.rf)
            else:
                # pricing_engine = QlBinomial(dt_eval, dt_maturity, OptionType.CALL, OptionExerciseType.AMERICAN, S, K,
                #                             rf=self.rf)
                pricing_engine = QlBAW(dt_eval, dt_maturity, OptionType.CALL, OptionExerciseType.AMERICAN, S, K,
                                       rf=self.rf)
            iv = pricing_engine.estimate_vol(C)
        else:
            P = df_series[Util.AMT_PUT_QUOTE]
            if self.exercise_type == OptionExerciseType.EUROPEAN:
                pricing_engine = QlBlackFormula(dt_eval, dt_maturity, OptionType.PUT, S, K, self.rf)
            else:
                # pricing_engine = QlBinomial(dt_eval, dt_maturity, OptionType.PUT, OptionExerciseType.AMERICAN, S, K,
                #                             rf=self.rf)
                pricing_engine = QlBAW(dt_eval, dt_maturity, OptionType.PUT, OptionExerciseType.AMERICAN, S, K,
                                       rf=self.rf)
            iv = pricing_engine.estimate_vol(P)
        return iv

    def get_htb_rate(self, dt_maturity, cd_option_price=Util.CD_CLOSE):
        t_qupte = self.get_T_quotes(dt_maturity, cd_option_price)
        t_qupte.loc[:, 'diff'] = abs(
            t_qupte.loc[:, Util.AMT_APPLICABLE_STRIKE] - t_qupte.loc[:, Util.AMT_UNDERLYING_CLOSE])
        atm_series = t_qupte.loc[t_qupte['diff'].idxmin()]
        htb_r = self.fun_htb_rate(atm_series, self.rf)
        return htb_r

    def fun_htb_rate(self, df_series, rf):
        r = -math.log((df_series[Util.AMT_CALL_QUOTE] - df_series[Util.AMT_PUT_QUOTE]
                       + df_series[Util.AMT_APPLICABLE_STRIKE] * math.exp(-rf * df_series[Util.AMT_TTM]))
                      / df_series[Util.AMT_UNDERLYING_CLOSE]) / df_series[Util.AMT_TTM]
        return r

    def fun_iv(self, df_series: pd.DataFrame, option_type: OptionType):
        K = df_series[Util.AMT_APPLICABLE_STRIKE]
        S = df_series[Util.AMT_UNDERLYING_CLOSE]
        dt_eval = df_series[Util.DT_DATE]
        dt_maturity = df_series[Util.DT_MATURITY]
        if option_type == OptionType.CALL:
            C = df_series[Util.AMT_CALL_QUOTE]
            if self.exercise_type == OptionExerciseType.EUROPEAN:
                pricing_engine = QlBlackFormula(dt_eval, dt_maturity, OptionType.CALL, S, K, self.rf)
            else:
                pricing_engine = QlBinomial(dt_eval, dt_maturity, OptionType.CALL, OptionExerciseType.AMERICAN, S, K,
                                            rf=self.rf)
                # pricing_engine = QlBAW(dt_eval, dt_maturity, OptionType.CALL, OptionExerciseType.AMERICAN, S, K,
                #                             rf=self.rf)
            iv = pricing_engine.estimate_vol(C)
        else:
            P = df_series[Util.AMT_PUT_QUOTE]
            if self.exercise_type == OptionExerciseType.EUROPEAN:
                pricing_engine = QlBlackFormula(dt_eval, dt_maturity, OptionType.PUT, S, K, self.rf)
            else:
                pricing_engine = QlBinomial(dt_eval, dt_maturity, OptionType.PUT, OptionExerciseType.AMERICAN, S, K,
                                            rf=self.rf)
                # pricing_engine = QlBAW(dt_eval, dt_maturity, OptionType.PUT, OptionExerciseType.AMERICAN, S, K,
                #                               rf=self.rf)
            iv = pricing_engine.estimate_vol(P)
        return iv

    def get_option_closest_strike(self,option_type:OptionType, target:float, maturity: datetime.date):
        mdt_calls, mdt_puts = self.get_orgnized_option_dict_for_moneyness_ranking()
        if option_type == OptionType.CALL:
            mdt_options_dict = mdt_calls.get(maturity)
        else:
            mdt_options_dict = mdt_puts.get(maturity)
        option = None
        min_diff = 100
        for k in mdt_options_dict.keys():
            if abs(k-target) < min_diff:
                min_diff = abs(k-target)
                option = mdt_options_dict[k]
        return option

    def get_option_by_strike(self,option_type:OptionType, strike:float, maturity: datetime.date):
        mdt_calls, mdt_puts = self.get_orgnized_option_dict_for_moneyness_ranking()
        if option_type ==OptionType.CALL:
            mdt_options_dict = mdt_calls.get(maturity)
        else:
            mdt_options_dict = mdt_puts.get(maturity)
        if strike not in mdt_options_dict.keys():
            return
        else:
            return mdt_options_dict[strike]

    def get_option_moneyness(self, base_option: BaseOption):
        maturity = base_option.maturitydt()
        mdt_calls, mdt_puts = self.get_orgnized_option_dict_for_moneyness_ranking()
        if base_option.option_type() == OptionType.CALL:
            mdt_options_dict = mdt_calls.get(maturity)
        else:
            mdt_options_dict = mdt_puts.get(maturity)
        spot = list(mdt_options_dict.values())[0][0].underlying_close()
        moneyness = self.OptionUtilClass.get_moneyness_of_a_strike_by_nearest_strike(spot, base_option.strike(),
                                                                                     list(mdt_options_dict.keys()),
                                                                                     base_option.option_type())
        return moneyness

    # 行权价最低的put
    def get_deepest_otm_put_list(self, maturity: datetime.date):
        mdt_calls, mdt_puts = self.get_orgnized_option_dict_for_moneyness_ranking()
        mdt_options_dict = mdt_puts.get(maturity)
        min_k = min(mdt_options_dict.keys())
        put_list = mdt_options_dict[min_k]
        return put_list

    """
    get_orgnized_option_dict_for_moneyness_ranking : 
    Dictionary <maturity-<nearest strike - List[option]>> to retrieve call and put List[option] by maturity date.
    call_mdt_option_dict:
    {
        '2017-05-17':{
            "2.8": [option1,option2],
            "2.85": [option1,option2],
        },
        '2017-06-17':{
            "2.8": [option1,option2],
            "2.85": [option1,option2],
        },
    }
    """

    def get_orgnized_option_dict_for_moneyness_ranking(self) -> \
            Tuple[
                Dict[datetime.date, Dict[float, List[BaseOption]]], Dict[datetime.date, Dict[float, List[BaseOption]]]]:
        call_ret = {}
        put_ret = {}
        for option in self.eligible_options:
            if option.option_type() == OptionType.CALL:
                ret = call_ret
            else:
                ret = put_ret
            d = ret.get(option.maturitydt())
            if d is None:
                d = {}
                ret.update({option.maturitydt(): d})
            l = d.get(option.nearest_strike())
            if l is None:
                l = []
                d.update({option.nearest_strike(): l})
            l.append(option)
        # 返回的option放在list里，是因为可能有相邻行权价的期权同时处于一个nearest strike
        return call_ret, put_ret

    def get_dict_moneyness_and_options(self, dt_maturity: datetime.date, option_type: OptionType) -> Dict[
        int, List[BaseOption]]:
        mdt_calls, mdt_puts = self.get_orgnized_option_dict_for_moneyness_ranking()
        if option_type == OptionType.CALL:
            dict_strike_options = mdt_calls.get(dt_maturity)
        else:
            dict_strike_options = mdt_puts.get(dt_maturity)
        spot = list(dict_strike_options.values())[0][0].underlying_close()
        strikes = list(dict_strike_options.keys())
        dict_moneyness_strikes = Option50ETF.get_strike_monenyes_rank_dict_nearest_strike(spot, strikes,
                                                                                          OptionType.PUT)
        dict_res = {}
        for m in dict_moneyness_strikes:
            dict_res.update({m: dict_strike_options[dict_moneyness_strikes[m]]})
        return dict_res

    """ Mthd1: Determine atm option as the NEAREST strike from spot. 
        Get option maturity dictionary from all maturities by given moneyness rank. """

    def get_options_dict_by_mdt_moneyness_mthd1(
            self, moneyness_rank: int,cd_price=CdPriceType.CLOSE) -> List[Dict[datetime.date, List[BaseOption]]]:
        mdt_calls, mdt_puts = self.get_orgnized_option_dict_for_moneyness_ranking()
        call_mdt_dict = {}
        put_mdt_dict = {}
        for mdt in mdt_calls.keys():
            mdt_options_dict = mdt_calls.get(mdt)
            spot = list(mdt_options_dict.values())[0][0].get_underlying_price(cd_price)
            idx = self.OptionUtilClass.get_strike_by_monenyes_rank_nearest_strike(spot, moneyness_rank,
                                                                                  list(mdt_options_dict.keys()),
                                                                                  OptionType.CALL)
            call_mdt_dict.update({mdt: mdt_options_dict.get(idx)})
        for mdt in mdt_puts.keys():
            mdt_options_dict = mdt_puts.get(mdt)
            spot = list(mdt_options_dict.values())[0][0].get_underlying_price(cd_price)
            idx = self.OptionUtilClass.get_strike_by_monenyes_rank_nearest_strike(spot, moneyness_rank,
                                                                                  list(mdt_options_dict.keys()),
                                                                                  OptionType.PUT)
            put_mdt_dict.update({mdt: mdt_options_dict.get(idx)})
        return [call_mdt_dict, put_mdt_dict]

    """ Mthd1: Determine atm option as the NEAREST strike from spot. 
        Get options by given moneyness rank and maturity date. """

    # 返回的option放在list里，是因为50ETF option可能有相近行权价的期权同时处于一个nearest strike
    def get_options_list_by_moneyness_mthd1(
            self, moneyness_rank: int, maturity: datetime.date,cd_price=CdPriceType.CLOSE) \
            -> List[List[BaseOption]]:
        mdt_calls, mdt_puts = self.get_orgnized_option_dict_for_moneyness_ranking()
        mdt_options_dict = mdt_calls.get(maturity)
        spot = list(mdt_options_dict.values())[0][0].get_underlying_price(cd_price)
        k_call = self.OptionUtilClass.get_strike_by_monenyes_rank_nearest_strike(spot, moneyness_rank,
                                                                                 list(mdt_options_dict.keys()),
                                                                                 OptionType.CALL)
        call_list = mdt_options_dict.get(k_call)
        mdt_options_dict = mdt_puts.get(maturity)
        k_put = self.OptionUtilClass.get_strike_by_monenyes_rank_nearest_strike(spot, moneyness_rank,
                                                                                list(mdt_options_dict.keys()),
                                                                                OptionType.PUT)
        put_list = mdt_options_dict.get(k_put)
        return [call_list, put_list]

    """ Mthd2: Determine atm option as the nearest OTM strike from spot. 
        Get option maturity dictionary from all maturities by given moneyness rank. 
        # moneyness_rank：
        # 0：平值: call strike=大于spot值的最小行权价; put strike=小于spot值的最大行权价
        # -1：虚值level1：平值行权价往虚值方向移一档
        # 1: 实值level1： 平值新全价往实值方向移一档 """

    def get_options_dict_by_mdt_moneyness_mthd2(
            self, moneyness_rank: int,cd_price=CdPriceType.CLOSE) -> List[Dict[datetime.date, List[BaseOption]]]:
        mdt_calls, mdt_puts = self.get_orgnized_option_dict_for_moneyness_ranking()
        call_mdt_dict = {}
        put_mdt_dict = {}
        for mdt in mdt_calls.keys():
            mdt_options_dict = mdt_calls.get(mdt)
            spot = list(mdt_options_dict.values())[0][0].get_underlying_price(cd_price)
            idx = self.OptionUtilClass.get_strike_by_monenyes_rank_otm_strike(spot, moneyness_rank,
                                                                              list(mdt_options_dict.keys()),
                                                                              OptionType.CALL)
            call_mdt_dict.update({mdt: mdt_options_dict.get(idx)})
        for mdt in mdt_puts.keys():
            mdt_options_dict = mdt_puts.get(mdt)
            spot = list(mdt_options_dict.values())[0][0].get_underlying_price(cd_price)
            idx = self.OptionUtilClass.get_strike_by_monenyes_rank_otm_strike(spot, moneyness_rank,
                                                                              list(mdt_options_dict.keys()),
                                                                              OptionType.PUT)
            put_mdt_dict.update({mdt: mdt_options_dict.get(idx)})
        return [call_mdt_dict, put_mdt_dict]

    """ Mthd2: Determine atm option as the nearest OTM strike from spot. 
        Get options by given moneyness rank and maturity date. 
        # moneyness_rank：
        # 0：平值: call strike=大于spot值的最小行权价; put strike=小于spot值的最大行权价
        # -1：虚值level1：平值行权价往虚值方向移一档
        # 1: 实值level1： 平值新全价往实值方向移一档 """

    def get_options_list_by_moneyness_mthd2(self, moneyness_rank: int, maturity: datetime.date, cd_price=CdPriceType.CLOSE) \
            -> List[List[BaseOption]]:
        mdt_calls, mdt_puts = self.get_orgnized_option_dict_for_moneyness_ranking()
        mdt_options_dict = mdt_calls.get(maturity)
        spot = list(mdt_options_dict.values())[0][0].get_underlying_price(cd_price)
        idx_call = self.OptionUtilClass.get_strike_by_monenyes_rank_otm_strike(spot, moneyness_rank,
                                                                               list(mdt_options_dict.keys()),
                                                                               OptionType.CALL)
        call_list = mdt_options_dict.get(idx_call)
        mdt_options_dict = mdt_puts.get(maturity)
        idx_put = self.OptionUtilClass.get_strike_by_monenyes_rank_otm_strike(spot, moneyness_rank,
                                                                              list(mdt_options_dict.keys()),
                                                                              OptionType.PUT)
        put_list = mdt_options_dict.get(idx_put)
        return [call_list, put_list]

    def select_maturity_date(self, nbr_maturity, min_holding: int = 1):
        maturities = self.get_maturities_list()
        idx_start = 0
        if (maturities[idx_start] - self.eval_date).days < min_holding:
            idx_start += 1
        idx_maturity = idx_start + nbr_maturity
        if idx_maturity > len(maturities) - 1:
            return
        else:
            return maturities[idx_maturity]

    # TODO: MOVE TO CONSTENT
    def select_higher_volume(self, options: List[BaseOption]) -> BaseOption:
        volume0 = 0.0
        res_option = None
        if options is None: return
        for option in options:
            volume = option.trading_volume()
            if volume >= volume0: res_option = option
            volume0 = volume
        return res_option

    # TODO: USE TOLYER'S EXPANSION.
    def yield_decomposition(self):
        return
