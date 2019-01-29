from MachineLearning.model.LstmRnn import LstmRnn

lstm = LstmRnn(
    activation='tanh',
    train_length=20,
    feature_nbr=16,
    predict_length=3,
    loss='mean_squared_logarithmic_error'
)
lstm.load('data.csv')
lstm.build_three_lay_lstm_rnn()
lstm.train(epochs=100)
lstm.save()
# lstm.plot_single_value_prediction()
lstm.plot_sequence_prediction(2)
