from MachineLearning.model.LstmRnn import LstmRnn

lstm = LstmRnn(
    activation='tanh',
    train_length=20,
    feature_nbr=16,
    predict_length=3,
    loss='mean_squared_logarithmic_error'
)
lstm.load('data.csv')
lstm.restore()
print(lstm.win_ratio())
lstm.plot_single_value_prediction()
