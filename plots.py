'''
Created on Dec 7, 2017

@author: samper
'''
import __init__  # @UnusedImport
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

df = pd.read_hdf("BatteryTest_Rayovac_01.h5", 'df')

df['Hrs'] = df.index / (60.0 * 60.0)
df['CurrentA'] = df['CurrrentmA'] / 1000.0
df['PowerW'] = df['CurrentA'] * df['VoltageV']
df['PowermW'] = df['PowerW'] * 1000.0

dT = (df.index[-1] - df.index[0]) / (df.index.size - 1)

# need even number of datapoits so
if ((df.index.size % 2) > 0):
    mean_mW = np.mean(df['PowermW'].iloc[0:-1].values.reshape(-1,2), axis=1)
    mean_mA = np.mean(df['CurrrentmA'].iloc[0:-1].values.reshape(-1,2), axis=1)
else:
    mean_mW = np.mean(df['PowermW'].values.reshape(-1,2), axis=1)
    mean_mA = np.mean(df['CurrrentmA'].values.reshape(-1,2), axis=1)    

mWs = np.cumsum(mean_mW * dT)
mAs = np.cumsum(mean_mA * dT)

mWh  = mWs / (60.0 * 60.0)
mAh = mAs / (60.0 * 60.0)

time_hrs = (np.arange(len(mAh)) * dT * 2.0) / (60.0 * 60.0)

fig , host = plt.subplots()
fig.set_size_inches(16,9, forward=True)
fig.set_dpi(80)
fig.set_facecolor('w')
fig.set_edgecolor('k')

plt.plot(time_hrs, mAh, label='mAh')
plt.plot(time_hrs, mWh, label='mWh')
plt.legend()

plt.show()