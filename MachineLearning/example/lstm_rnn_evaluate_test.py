from MachineLearning.model.LstmRnn import LstmRnn


lstm = LstmRnn()
lstm.load('data.csv')
lstm.restore()
lstm.plot_single_value_prediction()