import pandas as pd
from sklearn import preprocessing
import numpy as np
from keras.callbacks import ReduceLROnPlateau, ModelCheckpoint
from keras.models import Sequential
from keras.layers import Dense, Dropout, LSTM, GRU
from keras.optimizers import Adam
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
    for i in range(0, m - max(train_length, predict_length)):
        x = values[i:i + train_length, 0:13]
        y = values[i:i + predict_length, 13]
        dataX.append(x)
        dataY.append(y)
    return np.array(dataX), np.array(dataY)


df_data = pd.read_csv('data.csv')
df = df_data[
    ["amt_open", "amt_close", "amt_high", "amt_low", "amt_trading_volume", "amt_trading_value",
     "alpha2", "alpha3", "alpha_量价背离", "alpha_开盘缺口", "alpha_异常交易量", "alpha_量幅背离", "vol"]]
train_length = 10
predict_length = 1
sample_rate = 0.6
df_normalize = normalize(df)
dataX, dataY = generate(df_normalize, train_length, predict_length)
l, _, _ = dataX.shape
_, m = dataY.shape
trainX, trainY = dataX[0:int(l * sample_rate), :, :], dataY[0:int(l * sample_rate), :]
testX, testY = dataX[int(l * sample_rate):, :, :], dataY[int(l * sample_rate):, :]
"""
Setup learning rate reduce and model checkpoint
"""
checkFile = 'model_weight.hdf5'
dropout_rate = 0.
activation = 'relu'
lr_reduce = ReduceLROnPlateau(monitor="val_loss", factor=0.1, min_lr=10e-10, patience=3,
                              verbose=1)
checkpoint = ModelCheckpoint(checkFile, monitor='val_loss', verbose=1, save_best_only=True, mode='max')
model = Sequential()
model.add(GRU(512, input_shape=(train_length, 13), dropout=dropout_rate, recurrent_dropout=dropout_rate,
              activation=activation, return_sequences=True))
model.add(LSTM(256, activation=activation, dropout=dropout_rate, recurrent_dropout=dropout_rate, return_sequences=True))
model.add(LSTM(128, activation=activation, dropout=dropout_rate, recurrent_dropout=dropout_rate))
model.add(Dense(64, activation=activation))
model.add(Dropout(dropout_rate))
model.add(Dense(predict_length))
model.compile(loss='mean_squared_error', optimizer=Adam(lr=0.001), metrics=['mean_squared_error'])
history = model.fit(trainX, trainY, epochs=100, batch_size=64, callbacks=[lr_reduce],
                    validation_data=(dataX, dataY))
model.save(checkFile)
predict_train = model.predict(trainX)
predict_test = model.predict(testX)
m, n = dataY.shape
date = range(m)
truth = dataY.transpose()[0].tolist()
train_date = range(len(predict_train))
predict_train_value = predict_train.transpose()[0].tolist()
test_date = range(len(predict_train), m)
predict_test_value = predict_test.transpose()[0].tolist()
plt.plot(date, truth, 'r')
plt.plot(train_date, predict_train_value, 'b')
plt.plot(test_date, predict_test_value, 'y')
plt.show()
