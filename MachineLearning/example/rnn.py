import pandas as pd
from sklearn import preprocessing
import numpy as np


def normalize(df: pd.DataFrame):
    df_ret = df.copy(deep=True)
    min_max_scaler = preprocessing.MinMaxScaler()
    df_ret["amt_open"] = min_max_scaler.fit_transform(df.loc[:, "amt_open"].values.reshape(-1, 1))
    df_ret["amt_close"] = min_max_scaler.fit_transform(df.loc[:, "amt_close"].values.reshape(-1, 1))
    df_ret["amt_high"] = min_max_scaler.fit_transform(df.loc[:, "amt_open"].values.reshape(-1, 1))
    df_ret["amt_low"] = min_max_scaler.fit_transform(df.loc[:, "amt_low"].values.reshape(-1, 1))
    df_ret["amt_trading_volume"] = min_max_scaler.fit_transform(df.loc[:, "amt_trading_volume"].values.reshape(-1, 1))
    df_ret["amt_trading_value"] = min_max_scaler.fit_transform(df.loc[:, "amt_trading_value"].values.reshape(-1, 1))
    df_ret["alpha2"] = min_max_scaler.fit_transform(df.loc[:, "alpha2"].values.reshape(-1, 1))
    df_ret["alpha3"] = min_max_scaler.fit_transform(df.loc[:, "alpha3"].values.reshape(-1, 1))
    df_ret["alpha_量价背离"] = min_max_scaler.fit_transform(df.loc[:, "alpha_量价背离"].values.reshape(-1, 1))
    df_ret["alpha_开盘缺口"] = min_max_scaler.fit_transform(df.loc[:, "alpha_开盘缺口"].values.reshape(-1, 1))
    df_ret["alpha_异常交易量"] = min_max_scaler.fit_transform(df.loc[:, "alpha_异常交易量"].values.reshape(-1, 1))
    df_ret["alpha_量幅背离"] = min_max_scaler.fit_transform(df.loc[:, "alpha_量幅背离"].values.reshape(-1, 1))
    df_ret["normalized_vol"] = min_max_scaler.fit_transform(df.loc[:, "vol"].values.reshape(-1, 1))
    return df_ret[
        ["amt_open", "amt_close", "amt_high", "amt_low", "amt_trading_volume", "amt_trading_value",
         "alpha2", "alpha3", "alpha_量价背离", "alpha_开盘缺口", "alpha_异常交易量", "alpha_量幅背离", "normalized_vol", "vol"]]


def generate(df: pd.DataFrame, sequence_step=5):
    dataX, dataY = [], []
    values = df.values
    m, n = df.shape
    for i in range(0, m - sequence_step):
        x = values[i:i + 5, 0:13]
        y = values[i:i + 5, 13]
        dataX.append(x)
        dataY.append(y)
    return np.array(dataX), np.array(dataY)


df_data = pd.read_csv('data.csv')
df = df_data[
    ["amt_open", "amt_close", "amt_high", "amt_low", "amt_trading_volume", "amt_trading_value",
     "alpha2", "alpha3", "alpha_量价背离", "alpha_开盘缺口", "alpha_异常交易量", "alpha_量幅背离", "vol"]]
df_normalize = normalize(df)
dataX, dataY = generate(df_normalize)
print(dataY.shape)
l, _, _ = dataX.shape
_, m = dataY.shape
trainX, trainY = dataX[0:int(l * 0.8), :, :], dataY[0:int(l * 0.8), :]
testX, testY = dataX[int(l * 0.8):, :, :], dataY[int(l * 0.8):, :]
trainY = trainY.reshape(trainY.shape[0], 1, trainY.shape[1])
testY = testY.reshape(testY.shape[0], 1, testY.shape[1])
print(trainX.shape)
print(trainY.shape)
print(testX.shape)
print(testY.shape)
