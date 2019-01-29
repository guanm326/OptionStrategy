from MachineLearning.model.LstmRnn import LstmRnn

lstm = LstmRnn()
lstm.load('data.csv')
lstm.build_three_lay_lstm_rnn()
lstm.train()
lstm.save()
lstm.plot_single_value_prediction()
