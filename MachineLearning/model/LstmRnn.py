import pandas as pd
import numpy as np
from sklearn import preprocessing
from keras.callbacks import ReduceLROnPlateau
from keras.models import Sequential, load_model
from keras.layers import Dense, Dropout, LSTM, GRU
from keras.optimizers import Adam
import matplotlib.pyplot as plt


class LstmRnn:

    def __init__(self, train_length=10, predict_length=1, split_rate=0.6, droprate=0., activation='relu',
                 model_path='model_weight.dat', verbose=False):
        self.train_lenth = train_length
        self.predict_lenth = predict_length
        self.split_rate = split_rate
        self.droprate = droprate
        self.activation = activation
        self.model_path = model_path
        self.verbose = verbose
        self.data_x = None
        self.data_y = None
        self.train_x = None
        self.train_y = None
        self.test_x = None
        self.test_y = None
        self.model = None

    def normalize(self, df: pd.DataFrame):
        df_ret = df.copy(deep=True)
        min_max_scaler = preprocessing.MinMaxScaler()
        df_ret["amt_open"] = min_max_scaler.fit_transform(df.loc[:, "amt_open"].values.reshape(-1, 1))
        df_ret["amt_close"] = min_max_scaler.fit_transform(df.loc[:, "amt_close"].values.reshape(-1, 1))
        df_ret["amt_high"] = min_max_scaler.fit_transform(df.loc[:, "amt_open"].values.reshape(-1, 1))
        df_ret["amt_low"] = min_max_scaler.fit_transform(df.loc[:, "amt_low"].values.reshape(-1, 1))
        df_ret["amt_trading_volume"] = min_max_scaler.fit_transform(
            df.loc[:, "amt_trading_volume"].values.reshape(-1, 1))
        df_ret["amt_trading_value"] = min_max_scaler.fit_transform(df.loc[:, "amt_trading_value"].values.reshape(-1, 1))
        df_ret["alpha2"] = min_max_scaler.fit_transform(df.loc[:, "alpha2"].values.reshape(-1, 1))
        df_ret["alpha3"] = min_max_scaler.fit_transform(df.loc[:, "alpha3"].values.reshape(-1, 1))
        df_ret["alpha_量价背离"] = min_max_scaler.fit_transform(df.loc[:, "alpha_量价背离"].values.reshape(-1, 1))
        df_ret["alpha_开盘缺口"] = min_max_scaler.fit_transform(df.loc[:, "alpha_开盘缺口"].values.reshape(-1, 1))
        df_ret["alpha_异常交易量"] = min_max_scaler.fit_transform(df.loc[:, "alpha_异常交易量"].values.reshape(-1, 1))
        df_ret["alpha_量幅背离"] = min_max_scaler.fit_transform(df.loc[:, "alpha_量幅背离"].values.reshape(-1, 1))
        df_ret["alpha_my0"] = min_max_scaler.fit_transform(df.loc[:, "alpha_my0"].values.reshape(-1, 1))
        df_ret["alpha_my1"] = min_max_scaler.fit_transform(df.loc[:, "alpha_my1"].values.reshape(-1, 1))
        df_ret["normalized_vol"] = min_max_scaler.fit_transform(df.loc[:, "vol"].values.reshape(-1, 1))
        return df_ret[
            ["amt_open", "amt_close", "amt_high", "amt_low", "amt_trading_volume", "amt_trading_value",
             "alpha2", "alpha3", "alpha_量价背离", "alpha_开盘缺口", "alpha_异常交易量", "alpha_量幅背离", "alpha_my0", "alpha_my1",
             "normalized_vol", "vol"]]

    def generate(self, df: pd.DataFrame, train_length=5, predict_length=3):
        data_x, data_y = [], []
        values = df.values
        m, n = df.shape
        for i in range(0, m - max(train_length, predict_length)):
            x = values[i:i + train_length, 0:15]
            y = values[i:i + predict_length, 15]
            data_x.append(x)
            data_y.append(y)
        return np.array(data_x), np.array(data_y)

    def load(self, path='data.csv'):
        df_data = pd.read_csv(path)
        df = df_data[
            ["amt_open", "amt_close", "amt_high", "amt_low", "amt_trading_volume", "amt_trading_value",
             "alpha2", "alpha3", "alpha_量价背离", "alpha_开盘缺口", "alpha_异常交易量", "alpha_量幅背离", "alpha_my0", "alpha_my1",
             "vol"]]
        df_normalize = self.normalize(df)
        self.data_x, self.data_y = self.generate(df_normalize, self.train_lenth, self.predict_lenth)
        l, _, _ = self.data_x.shape
        _, m = self.data_y.shape
        self.train_x, self.train_y = self.data_x[0:int(l * self.split_rate), :, :], self.data_y[
                                                                                    0:int(l * self.split_rate), :]
        self.test_x, self.test_y = self.data_x[int(l * self.split_rate):, :, :], self.data_y[int(l * self.split_rate):,
                                                                                 :]
        if self.verbose:
            print("#####DataPreview#####")
            print("All data x")
            print(self.data_x.shape)
            print("All data y")
            print(self.data_y.shape)
            print("Training data x")
            print(self.train_x.shape)
            print("Training data y")
            print(self.train_y.shape)
            print("Testing data x")
            print(self.test_x.shape)
            print("Testing data y")
            print(self.test_y.shape)

    """
    Build a toy rnn with three layers of GRU, LSTM, LSTM network
    """

    def build_three_lay_lstm_rnn(self):
        self.model = Sequential()
        self.model.add(GRU(512, input_shape=(self.train_lenth, 15), dropout=self.droprate,
                           recurrent_dropout=self.droprate, activation=self.activation, return_sequences=True))
        self.model.add(LSTM(256, activation=self.activation, dropout=self.droprate, recurrent_dropout=self.droprate,
                            return_sequences=True))
        self.model.add(LSTM(128, activation=self.activation, dropout=self.droprate, recurrent_dropout=self.droprate))
        self.model.add(Dense(64, activation=self.activation))
        self.model.add(Dropout(self.droprate))
        self.model.add(Dense(self.predict_lenth))
        self.model.compile(loss='mean_squared_error', optimizer=Adam(lr=0.001), metrics=['mean_squared_error'])
        if self.verbose:
            print("#####DataPreview#####")
            print(self.model.summary())

    """
    Build a toy rnn with four layers of GRU, LSTM, LSTM, LSTM network
    """

    def build_four_lay_lstm_rnn(self):
        self.model = Sequential()
        self.model.add(GRU(1024, input_shape=(self.train_lenth, 15), dropout=self.droprate,
                           recurrent_dropout=self.droprate, activation=self.activation, return_sequences=True))
        self.model.add(LSTM(512, activation=self.activation, dropout=self.droprate, recurrent_dropout=self.droprate,
                            return_sequences=True))
        self.model.add(LSTM(256, activation=self.activation, dropout=self.droprate, recurrent_dropout=self.droprate,
                            return_sequences=True))
        self.model.add(LSTM(128, activation=self.activation, dropout=self.droprate, recurrent_dropout=self.droprate))
        self.model.add(Dense(64, activation=self.activation))
        self.model.add(Dropout(self.droprate))
        self.model.add(Dense(self.predict_lenth))
        self.model.compile(loss='mean_squared_error', optimizer=Adam(lr=0.001), metrics=['mean_squared_error'])
        if self.verbose:
            print("#####DataPreview#####")
            print(self.model.summary())

    """
    Train the model
    """

    def train(self, epochs=100, batch_size=64):
        self.check()
        lr_reduce = ReduceLROnPlateau(monitor="val_loss", factor=0.1, min_lr=10e-10, patience=3, verbose=1)
        self.model.fit(self.train_x, self.train_y, epochs=epochs, batch_size=batch_size, callbacks=[lr_reduce],
                       validation_data=(self.test_x, self.test_y))

    """
    Save model to file
    """

    def save(self):
        self.model.save(self.model_path)

    """
    Restore model from file
    """

    def restore(self):
        self.model = load_model(self.model_path)

    """
    Make a plot of single value prediction comparing ground truth (data_y) with prediction on training set and testing set
    """

    def plot_single_value_prediction(self):
        predict_train = self.model.predict(self.train_x)
        predict_test = self.model.predict(self.test_x)
        m, n = self.data_y.shape
        date = range(m)
        truth = self.data_y.transpose()[0].tolist()
        train_date = range(len(predict_train))
        predict_train_value = predict_train.transpose()[0].tolist()
        test_date = range(len(predict_train), m)
        predict_test_value = predict_test.transpose()[0].tolist()
        plt.plot(date, truth, 'r')
        plt.plot(train_date, predict_train_value, 'b')
        plt.plot(test_date, predict_test_value, 'y')
        plt.show()

    """
    Make a plot of sequence prediction comparing ground truth (data_y) with prediction on training set and testing set
    """

    def plot_sequence_prediction(self, output_sample_factor=5):
        predict_train = self.model.predict(self.train_x)
        predict_test = self.model.predict(self.test_x)
        m, n = self.data_y.shape
        date = range(m)
        truth = self.data_y.transpose()[0].tolist()
        plot_train = []
        plot_test = []
        # Only plot 1 of 5 sequence here to avoid overlap
        for i in range(predict_train.shape[0]):
            if i % output_sample_factor != 0:
                continue
            t = dict()
            t['x'] = range(i, i + self.predict_lenth)
            t['y'] = predict_train[i]
            plot_train.append(t)
        bias = predict_train.shape[0]
        for i in range(predict_test.shape[0]):
            if i % output_sample_factor != 0:
                continue
            t = dict()
            t['x'] = range(bias + i, bias + i + self.predict_lenth)
            t['y'] = predict_test[i]
            plot_test.append(t)

        plt.plot(date, truth, 'r')
        for p in plot_train:
            plt.plot(p['x'], p['y'], 'b')
        for p in plot_test:
            plt.plot(p['x'], p['y'], 'y')
        plt.show()

    """
    Check if required data is missing
    """

    def check(self):
        if self.train_x is None or self.train_y is None or self.test_x is None or self.test_y is None or self.model is None:
            raise ValueError("Either dataset or model is missing.")
