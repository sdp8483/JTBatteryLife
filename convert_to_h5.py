'''
Created on Dec 5, 2017

@author: samper

Convert windaq files (.wdq extension) to Python freindly hd5f store file as pandas dataframe
    
Code based on http://www.dataq.com/resources/pdfs/misc/ff.pdf provided by Dataq, code and comments will refer to conventions from this file 
and python library https://www.socsci.ru.nl/wilberth/python/wdq.py that does not appear to support the .wdq files created by WINDAQ/PRO+
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