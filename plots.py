'''
Created on Dec 7, 2017

@author: samper

Generate Plots from Joule Thief Measurments of
    - Voltage, Current, and Power
    - mAh, mWh
'''
from datetime import datetime
start_of_processing = datetime.now()

import __init__  # @UnusedImport
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

v_cutoff = 0.4327                                                       # marks end of continuous drain

''' Import data from h5 file '''
#df_import = pd.read_hdf("C:/Users/Sam/Python/Fun/JTBatteryLife/BatteryTest_Rayovac_01.h5", 'df')
df_import = pd.read_hdf("BatteryTest_Rayovac_01.h5", 'df')

df_temp = df_import[df_import['Voltage_V'] > 0.0]                       # remove negative voltage from begining of data
v_cutoff_index = df_temp[df_temp['Voltage_V'] < v_cutoff].index[0]      # index location of first voltage < 0.4327
df = df_temp.drop(df_temp.loc[v_cutoff_index:].index)                   # remove non continus discharge at end of data

df['Hrs'] = df.index / (60.0 * 60.0)                                    # index is in seconds, want smaller time numbers
df['Current_A'] = df['Current_mA'] / 1000.0                             # convert mA to A for power calculation
df['Power_W'] = df['Current_A'] * df['Voltage_V']                       # power = V * I
df['Power_mW'] = df['Power_W'] * 1000.0                                 # power in mW

dT = (df.index[-1] - df.index[0]) / (df.index.size - 1)                 # get time step for integration to calculate mAh ans mWh

''' plot of voltage, current, and power '''
fig , axs = plt.subplots(3,1, sharex=True)
fig.subplots_adjust(hspace=0.1)
fig.set_size_inches(16,9, forward=True)
fig.set_dpi(80)
fig.set_facecolor('w')
fig.set_edgecolor('k')

p1, = axs[0].plot(df['Hrs'], df['Voltage_V'], '-b', label='voltage')
axs[0].set_ylim(0, 2.0)
axs[0].set_yticks(np.arange(0, 2.1, 0.25))
axs[0].set_ylabel('Voltage [V]')

p2, = axs[1].plot(df['Hrs'], df['Current_mA'], '-g', label='current')
axs[1].set_ylim(0, 60.0)
axs[1].set_yticks(np.arange(0, 60.1, 5.0))
axs[1].set_ylabel('Current [mA]')

p3, = axs[2].plot(df['Hrs'], df['Power_mW'], '-m', label='power')
axs[2].set_ylim(0, 90.0)
axs[2].set_yticks(np.arange(0, 90.1, 10.0))
axs[2].set_xlabel("Time [hours]")
axs[2].set_ylabel('Power [mW]')

for ax in axs:
    ax.set_xlim(0, 105.0)                                               # only view continuos discharge data
    ax.set_xticks(np.arange(0, 105.1, 5.0))                             # set xtick spacing
    ax.grid()                                                           # turn on grid               

tkw = dict(size=4, width=1.5)    
for ax, p in zip(axs, [p1,p2,p3]):
    ax.yaxis.label.set_color(p.get_color())
    ax.tick_params(axis='y', colors=p.get_color(), **tkw)

plt.suptitle("Rayovac Battery Discharge \n 10Hz Sample Rate")

#plt.show()
plt.savefig("JT_power.png")
plt.close()

''' calculate mAh ans mWh '''
Ws = np.cumsum(df['Power_W'] * dT)                                      # integrate power for Ws
As = np.cumsum(df['Current_A'] * dT)                                    # integrate current for As

Wh  = Ws / (60.0 * 60.0)                                                # convert to Wh
mAh = (As / (60.0 * 60.0)) * 1000.0                                     # convert to Ah

time_hrs = (np.arange(len(Wh)) * dT) / (60.0 * 60.0)                    # use timestep (dT) to generate time axis

fig , axs2 = plt.subplots(2,1, sharex=True)
fig.subplots_adjust(hspace=0.1)
fig.set_size_inches(16,9, forward=True)
fig.set_dpi(80)
fig.set_facecolor('w')
fig.set_edgecolor('k')

q1, = axs2[0].plot(time_hrs, mAh, '-b', label='mAh')
axs2[0].set_ylim(0, 3500.0)
axs2[0].set_yticks(np.arange(0, 3500.1, 250.0))
axs2[0].set_ylabel('mAh')

q2, = axs2[1].plot(time_hrs, Wh, '-g', label='Wh')
axs2[1].set_ylim(0, 4.0)
axs2[1].set_yticks(np.arange(0, 4.1, 0.25))
axs2[1].set_xlabel("Time [hours]")
axs2[1].set_ylabel('Wh')                                    

for ax in axs2:
    ax.set_xlim(0, 105)                                                 # only view continuos discharge data     
    ax.set_xticks(np.arange(0, 105.1, 5.0))                             # set xtick spacing
    ax.grid()                                                           # turn on grid

for ax, q in zip(axs2, [q1, q2]):
    ax.yaxis.label.set_color(q.get_color())
    ax.tick_params(axis='y', colors=q.get_color(), **tkw)

plt.suptitle("Rayovac Battery Capacity \n in Multi-LED Joule Thief Circuit")

#plt.show()
plt.savefig("JT_capacity.png")
plt.close()

print "{} Wh".format(Wh.max())
print "{} mAh\n".format(mAh.max())

print datetime.now() - start_of_processing