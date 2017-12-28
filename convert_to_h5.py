'''
Created on Dec 5, 2017

@author: samper

convert WDQ file to h5 file for use with python
'''
from datetime import datetime
start_of_processing = datetime.now()

import windaq as w

''' Convert '''

data_dir = "windaq/"

data_files = ["BatteryTest_Rayovac_01.WDH"]

for data in data_files:
    print data,
    df = w.convertWindaq("{}{}".format(data_dir, data))
    print "open"
    df.to_hdf("{}".format(data.replace('.WDH', '.h5')), "df")
    del df

print datetime.now() - start_of_processing