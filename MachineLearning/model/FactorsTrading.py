from MachineLearning.util import Util
import pandas as pd
import numpy as np


class Factors:

    @staticmethod
    def alpha_2(data_array,i=0):
        [close, open, high, low, volume, value] = data_array
        a0 = ((close[i+0]-low[i+0])-(high[i+0]-close[i+0]))/(high[i+0]-low[i+0])
        a1 = ((close[i+1]-low[i+1])-(high[i+1]-close[i+1]))/(high[i+1]-low[i+1])
        delta_a = a0-a1
        res = -1*delta_a
        return res

    @staticmethod
    def alpha_3(data_array,i=0):
        [close, open, high, low, volume, value] = data_array
        res = 0
        for j in i + np.arange(6):
            if close[j+0] == close[j+1]:
                a = 0
            else:
                if close[j+0] > close[j+1]:
                    a = close[j+0] - min(low[j+0],close[j+1])
                else:
                    a = close[j+0] - max(high[j+0],close[j+1])
            res += a
            print(j,a)
        return res

