from MachineLearning.model.LstmRnn import LstmRnn

lstm = LstmRnn(activation='elu')
lstm.load('data.csv')
lstm.build_five_lay_lstm_rnn()
lstm.train(epochs=100)
lstm.save()
lstm.plot_single_value_prediction()
