import math
import matplotlib.pyplot as plt
import numpy as np
import back_test.model.constant as c
import pandas as pd
import datetime
from Utilities.PlotUtil import PlotUtil
import math

df_simulation_npvs_bad = pd.read_csv('../../accounts_data/df_simulation_npvs_1000_2008.csv')
df_simulation_analysis_bad = pd.read_csv('../../accounts_data/df_simulation_analysis_1000_2008.csv')
max_absolute_loss = list(df_simulation_analysis_bad['max_absolute_loss'])
annual_yield = list(df_simulation_analysis_bad['annual_yield'])
df_1 = df_simulation_analysis_bad[df_simulation_analysis_bad['max_absolute_loss']>=-0.1]
print('Historical Simulation by 2008')
print('Mean annual_yield : ', round(np.mean(annual_yield),2))
# print('Mean annual_yield : ', np.mean(annual_yield))
print('Mean max_absolute_loss : ', round(np.mean(max_absolute_loss),2))
print('Prob. max_absolute_loss >= -10% : ', len(df_1)/len(df_simulation_analysis_bad))
print('')

plt.figure()
plt.hist(max_absolute_loss, bins=100, density=True, facecolor="#CC0000", label="max absolute loss (historical simulation by 2008)")
plt.legend()
plt.figure()
plt.hist(annual_yield, bins=100, density=True, facecolor="#CC0000", label="annual yield (historical simulation by 2008)")
plt.legend()

df_simulation_npvs_good = pd.read_csv('../../accounts_data/df_simulation_npvs_1000_2007.csv')
df_simulation_analysis_good = pd.read_csv('../../accounts_data/df_simulation_analysis_1000_2007.csv')
max_absolute_loss = list(df_simulation_analysis_good['max_absolute_loss'])
annual_yield = list(df_simulation_analysis_good['annual_yield'])
df_1 = df_simulation_analysis_good[df_simulation_analysis_good['max_absolute_loss']>=-0.1]
print('Historical Simulation by 2007')
print('Mean annual_yield : ', round(np.mean(annual_yield),2))
print('Mean max_absolute_loss : ', round(np.mean(max_absolute_loss),2))
print('Prob. max_absolute_loss >= -10% : ', len(df_1)/len(df_simulation_analysis_good))

plt.figure()
plt.hist(max_absolute_loss, bins=100, density=True, facecolor="#CC0000", label="max absolute loss (historical simulation by 2007)")
plt.legend()
plt.figure()
plt.hist(annual_yield, bins=100, density=True, facecolor="#CC0000", label="annual yield (historical simulation by 2007)")
plt.legend()
plt.show()
