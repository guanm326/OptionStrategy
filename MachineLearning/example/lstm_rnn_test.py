from MachineLearning.model.LstmRnn import LstmRnn

lstm = LstmRnn()
lstm.load('data.csv')
lstm.build_four_lay_lstm_rnn()
lstm.train(epochs=1)
lstm.save()
# lstm.restore()
lstm.plot_single_value_prediction()
