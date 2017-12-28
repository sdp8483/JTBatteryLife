'''
Created on Dec 28, 2017

@author: Sam

Convert windaq files (.wdq extension) to Python freindly hd5f store file as pandas dataframe
    
Code based on http://www.dataq.com/resources/pdfs/misc/ff.pdf provided by Dataq, code and comments will refer to conventions from this file 
and python library https://www.socsci.ru.nl/wilberth/python/wdq.py that does not appear to support the .wdq files created by WINDAQ/PRO+
'''
import struct
import numpy as np
import pandas as pd
from datetime import datetime

''' Define data types based off convention used in documentation from Dataq '''
UI = "<H" # unsigned integer, little endian
I  = "<h" # integer, little endian
B  = "B"  # unsigned byte, kind of reduntent but lets keep consistant with the documentation
UL = "<L" # unsigned long, little endian
D  = "<d" # double, little endian
L  = "<l" # long, little endian
F  = "<f" # float, little endian

def convertWindaq(filename):
    with open(filename, 'rb') as _file:
        _fcontents = _file.read()
    
    ''' Read Header Info '''
    if (struct.unpack_from(B, _fcontents, 1)[0]):                       # if byte 1 of element 1 is 1 then max_channels >= 144
        nChannels = struct.unpack_from(B, _fcontents, 0)[0]             # number of channels is byte 0 of element 1
    else:                                                               # else max_channels = 29
        nChannels = (struct.unpack_from(B, _fcontents, 0)[0]) & 31      # number of channels is byte 0 of element 1 with b5 masked 
    
    hChannels       = struct.unpack_from(B,  _fcontents, 4)[0]          # offset in bytes from BOF to header channel info tables
    hChannelSize    = struct.unpack_from(B,  _fcontents, 5)[0]          # number of bytes in each channel info entry
    headSize        = struct.unpack_from(I,  _fcontents, 6)[0]          # number of bytes in data file header
    dataSize        = struct.unpack_from(UL, _fcontents, 8)[0]          # number of ADC data bytes in file excluding header
    nSample         = (dataSize/(2 * nChannels))                        # number of samples per channel
    trailerSize     = struct.unpack_from(UL, _fcontents,12)[0]          # total number of event marker, time and date stamp, and event marker commet pointer bytes in trailer
    annoSize        = struct.unpack_from(UI, _fcontents, 16)[0]         # toatl number of usr annotation bytes including 1 null per channel
    timeStep        = struct.unpack_from(D,  _fcontents, 28)[0]         # time between channel samples: 1/(sample rate throughput / total number of acquired channels)
    #e14             = struct.unpack_from(L,  _fcontents, 36)[0]         # time file was opened by acquisition: total number of seconds since jan 1 1970
    #e15             = struct.unpack_from(L,  _fcontents, 40)[0]         # time file was written by acquisition: total number of seconds since jan 1 1970
    #fileCreated     = getDatetime(e14)                                  # datetime format of time file was opened by acquisition
    #fileWritten     = getDatetime(e15)                                  # datetime format of time file was written by acquisition
    e27             = struct.unpack_from(UI, _fcontents, 100)[0]        # element 27

    ''' read channel info '''
    scalingSlope       = []
    scalingIntercept   = []
    calScaling         = []
    calIntercept       = []
    engUnits           = []
    sampleRateDivisor  = []
    phyChannel         = []
    
    for channel in range(0, nChannels):
        channelOffset = hChannels + (hChannelSize * channel)                                        # calculate channel header offset from beginging of file, each channel header size is defined in _hChannelSize
        scalingSlope.append(struct.unpack_from(F, _fcontents, channelOffset)[0])                    # scaling slope (m) applied to the waveform to scale it within the display window
        scalingIntercept.append(struct.unpack_from(F,_fcontents, channelOffset + 4)[0])             # scaling intercept (b) applied to the waveform to scale it withing the display window
        calScaling.append(struct.unpack_from(D, _fcontents, channelOffset + 4 + 4)[0])              # calibration scaling factor (m) for waveforem vale dispaly
        calIntercept.append(struct.unpack_from(D, _fcontents, channelOffset + 4 + 4 + 8)[0])        # calibration intercept factor (b) for waveform value display
        engUnits.append(struct.unpack_from("cccccc", _fcontents, channelOffset + 4 + 4 + 8 + 8))    # engineering units tag for calibrated waveform, only 4 bits are used last two are null
        
        if isPacked(e27):                                                                                        #  if file is packed then item 7 is the sample rate divisor
            sampleRateDivisor.append(struct.unpack_from(B, _fcontents, channelOffset + 4 + 4 + 8 + 8 + 6 + 1)[0])
        else:
            sampleRateDivisor.append(1)
        
        phyChannel.append(struct.unpack_from(B, _fcontents, channelOffset + 4 + 4 + 8 + 8 + 6 + 1 + 1)[0])        # describes the physical channel number
    
    ''' read user annotations '''
    aOffset = headSize + dataSize + trailerSize
    aTemp = ''
    for i in range(0, annoSize):
        aTemp += struct.unpack_from('c', _fcontents, aOffset + i)[0]
        for uchar in ['[', ']', ' ']:
            aTemp = aTemp.replace(uchar, '')
    annotations = aTemp.split('\x00')
    
    ''' create the time series '''
    #td_series = pd.to_timedelta((np.arange(nSample) * timeStep), unit='s') # to_timedelta is slow
    td_series = np.array(np.arange(nSample) * timeStep)
    
    df = pd.DataFrame()
    for channel in np.arange(nChannels):
        dataOffset = headSize + ((channel) * 2)
        channelIndex = dataOffset + (2 * nChannels * np.arange(nSample))
        s = pd.Series(
                        np.array([struct.unpack_from(I, _fcontents, ci)[0] for ci in channelIndex]),
                        index = td_series,
                        name = annotations[channel],
                      )
        
        if isHiRes(e27):
            s = s * 0.25 # multiply by 0.25 for HiRes data
            
        else:
            s = np.right_shift(s, 2)              # bit shift by two for normal data
    
        s = calScaling[channel] * s + calIntercept[channel]
        df = pd.concat([df, s], axis=1)
        
        del s, channelIndex, dataOffset
        
    return df

def isPacked(element_27):
    bit_14 = ((element_27) & 16384) >> 14
    
    if (bit_14 == 1):
        return True
    else:
        return False

def isHiRes(element_27):
    bit_1 = (element_27) & 1
    
    if (bit_1 == 1):
        return True
    else:
        return False

def getDatetime(element):
    return datetime.fromtimestamp(element).strftime('%Y-%m-%d %H:%M:%S')
