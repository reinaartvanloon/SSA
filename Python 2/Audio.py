# -*- coding: utf-8 -*-
"""
Created on Wed Jan  8 16:48:34 2020

Requires [modules]:
    -wavfile
    -simpleaudio
    -numpy

Contains:
    -randomsignal(size)
    -adapt
    -read_audiofile
    -decodereceive
    
@author: arozenevallesp
"""


import numpy
# scipy for audio
from scipy.io import wavfile
import scipy.signal
stdofn = 1000


def randomsignal(size):
    """
    Create an array of random numbers, to test sending data
    """
    numpy.random.seed(1)
    values = 10000*numpy.random.rand(size)
    values = values.astype('int')
    return values


def adapt(adapt_data,loa):
    """
    adapt(adapt_data, length of chunk) takes a numpy array as input and 
    converts it to a 5 character string array with a signature element in the 
    end
    """
    adapted = [] 
    for ii in range(0,int(len(adapt_data)-loa+1),loa):
        prepare = ''    
        for jj in range(loa-1):    
            prepare+=str(adapt_data[ii+jj])+','
        adapted.append(bytes(prepare+'\n','ascii'))
    adapted[len(adapted)-1] = b'9.99\n'
    return adapted


def read_audiofile(audio_name,cutToLength):
    """
    Wrapper for wavfile.read(), cuts the audio file to a desired length and 
    downsamples the freqeuncy of the signal 
    """
    fs, data = wavfile.read(audio_name)
    # sa.play_buffer(audio_data, num_channels, bydeftes_per_sample,sample_rate)
    #play_obj = sa.play_buffer(data,1,2,fs)
    #play_obj.stop()
    # delete one column. Make mono channel
    if data.shape[1]>1:
        data = numpy.delete(data,1,1)
    #downsample if signal is broad
    if fs>24000:
        data = numpy.delete(data, numpy.s_[::2], 0)
        fs = int(fs/2)
    
    data = data[data!=0]
    data = numpy.delete(data,numpy.s_[ int(cutToLength*fs):len(data)] )
    return data

def decode_receive(raw_received):
    # hold list of lists
    line = []
    #delete the stop bit entry
    del raw_received[len(raw_received)-1]
    #amplitude_factor = 30
    
    #take out signal strength
    ssdb = [item for item in raw_received if len(item)<10]
    #ssdb = [item for item in ssdb if "-" not in item and "\r\n" not in item]
    ssdb = [itm for sbtm in ssdb for itm in sbtm.split() if itm.isdigit()]
    ssdb = [int(i) for i in ssdb]
        
    # take out signal 
    raw_received = [item for item in raw_received if len(item)>10]
    
    #re-arrange taking away the commas
    for x in range(0,len(raw_received)-1):
        #raw_received = raw_received[x].decode('ascii')
        line.append(raw_received[x].split(','))
    # list to hold flat list made of list of lists
    flat_list = []
    for sublist in line:
        for item in sublist:
            flat_list.append(item)
    
    #flat_list = [s.strip('\n') for s in flat_list]
    flat_list = [item for item in flat_list if "\n" not in item]
    test_list = [int(i) for i in flat_list]
    g = numpy.random.normal( size=len(test_list), scale=stdofn )

    noise_filtered = scipy.signal.lfilter( b=[1, -0.4],
                                           a=[1, -0.95],
                                           x=g )
    correlated_noise_filtered = scipy.signal.lfilter( b=[1, -0.5],
                                                      a=[1, -0.9],
                                                      x=g )
    correlated_noise_filtered = correlated_noise_filtered.astype('int16')
    
    amplitude_factor = 105000/numpy.std(test_list)
    processed = numpy.asarray(test_list)*(amplitude_factor/(sum(ssdb)/len(ssdb))) + \
                noise_filtered
    processed= processed.astype('int16')
    return processed, correlated_noise_filtered
