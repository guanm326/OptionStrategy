from MachineLearning.util import Util
import pandas as pd
import numpy as np


class Factors:

    @staticmethod
    def alpha_1(df:pd.Series):
        delta = np.log(df[Util.AMT_TRADING_VOLUME]).diff()

        return

