import pandas as pd
from sklearn import preprocessing
import numpy as np
from keras.models import load_model
import matplotlib.pyplot as plt


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


def generate(df: pd.DataFrame, train_length=5, predict_length=3):
    dataX, dataY = [], []
    values = df.values
    m, n = df.shape
    for i in range(0, m - (train_length + predict_length) + 1):
        x = values[i:i + train_length, 0:13]
        y = values[i + train_length:i + train_length + predict_length, 13]
        dataX.append(x)
        dataY.append(y)
    return np.array(dataX), np.array(dataY)


train_length = 10
predict_length = 1
sample_rate = 0.65
output_sample_factor = 5
df_data = pd.read_csv('data.csv')
df = df_data[
    ["amt_open", "amt_close", "amt_high", "amt_low", "amt_trading_volume", "amt_trading_value",
     "alpha2", "alpha3", "alpha_量价背离", "alpha_开盘缺口", "alpha_异常交易量", "alpha_量幅背离", "vol"]]
df_normalize = normalize(df)
dataX, dataY = generate(df_normalize, train_length, predict_length)
checkFile = 'model_weight.hdf5'
model = load_model(checkFile)
l, _, _ = dataX.shape
_, m = dataY.shape
trainX, trainY = dataX[0:int(l * sample_rate), :, :], dataY[0:int(l * sample_rate), :]
testX, testY = dataX[int(l * sample_rate):, :, :], dataY[int(l * sample_rate):, :]
predict_train = model.predict(trainX)
predict_test = model.predict(testX)
m, n = dataY.shape
date = range(m)
truth = dataY.transpose()[0].tolist()
train_date = range(len(predict_train))
plot_train = []
plot_test = []
for i in range(predict_train.shape[0]):
    if i % output_sample_factor != 0:
        continue
    t = dict()
    t['x'] = range(i, i + predict_length)
    t['y'] = predict_train[i]
    plot_train.append(t)
bias = predict_train.shape[0]
for i in range(predict_test.shape[0]):
    if i % output_sample_factor != 0:
        continue
    t = dict()
    t['x'] = range(bias + i, bias + i + predict_length)
    t['y'] = predict_test[i]
    plot_test.append(t)

plt.plot(date, truth, 'r')
for p in plot_train:
    plt.plot(p['x'], p['y'], 'b')
for p in plot_test:
    plt.plot(p['x'], p['y'], 'y')
plt.show()
# predict_train_value = predict_train.transpose()[0].tolist()
# test_date = range(len(predict_train), m)
# predict_test_value = predict_test.transpose()[0].tolist()
# plt.plot(date, truth, 'r')
# plt.plot(train_date, predict_train_value, 'b')
# plt.plot(test_date, predict_test_value, 'y')
# plt.show()
