# -*- coding: utf-8 -*-

import pyedflib
import numpy as np
import matplotlib.pyplot as plt
import re
import sys

class Fourier(object):
  def __init__(self, filename, Fs, channel, window, overlap, f_min, f_max, 
               t_min, t_max, reference1, reference2 = None, title = ''):
        
    self.filename = filename
    self.Fs = Fs
    self.reference1 = reference1
    self.reference2 = reference2
    self.channel = channel
    self.window = window
    self.overlap = overlap
    self.f_min = f_min
    self.f_max = f_max
    self.t_min = t_min
    self.t_max = t_max
    self.title = title
        
        
    self.read_from_edf()
    self.montage()
    self.spectrogram()
    self.TFRPlot()


  def read_from_edf(self): 
  
    print('Reading the data from edf file.')
    f = pyedflib.EdfReader(self.filename)
    Fs = self.Fs
    n = f.signals_in_file
    signal_label = f.getSignalLabels()
    self.signal = np.zeros((n, f.getNSamples()[0]))
    self.signal_labels = []
    for i in np.arange(n):
      self.signal[i, :] = f.readSignal(i)
      self.signal_labels.append(re.sub(r'\W','',str(signal_label[i])))
    self.time = np.arange(0, np.shape(self.signal)[1]/Fs, 1/Fs)
    f.close()

    return self.signal, self.time, self.signal_labels


  def montage(self):

    try:

      if self.reference2 == None:
        a1 = self.signal_labels.index(self.reference1)

        for i in range(np.shape(self.signal)[0]):
          self.signal[i] -= a1
  
      else:
        a1 = self.signal_labels.index(self.reference1)
        a2 = self.signal_labels.index(self.reference2)

        for i in range(np.shape(self.signal)[0]):
          self.signal[i] -= 0.5*(a1+a2)

    except:
      print("There is not such channel")
      sys.exit(1)

    return self.signal


  def spectrogram(self):

    try:
      x = self.signal[self.channel]
    except:
      print("There is not such channel")
      sys.exit(1)

    Nx = len(x)
    No = len(self.window)
    self.window = self.window/np.linalg.norm(self.window)
    window_pos = np.arange(0, Nx, self.overlap)                        
    self.time_map = window_pos/self.Fs
    N_windows = len(window_pos)                     #numbers of windows  
    self.freq_map = np.fft.rfftfreq(No, 1/self.Fs)
    self.power = np.zeros((len(self.freq_map),N_windows))
    z = np.zeros(int(No/2))                        #half of window to add to the begining and to the end
    sig = np.concatenate((z,x,z))
    for i,pos in enumerate(window_pos):
        s = sig[pos:pos+No] #part of the signal with len of the window
        s = s*self.window    #convolution
        S = np.fft.rfft(s)  
        Power_tmp = S*S.conj()    #power spectrum = S*S conjuction
        Power_tmp = Power_tmp.real/self.Fs    #The imaginary part is 0
        if len(s)%2 ==0: 
            Power_tmp[1:-1] *=2
        else:
            Power_tmp[1:] *=2 
        self.power[:,i] = Power_tmp
    return self.time_map, self.freq_map, self.power

    
  def TFRPlot(self):
      
      df = self.freq_map[1]-self.freq_map[0]
      dt = self.time_map[1]-self.time_map[0]

      f_min_m = min(self.freq_map, key=lambda x:abs(x-self.f_min))
      f_max_m = min(self.freq_map, key=lambda x:abs(x-self.f_max))
      t_min_m = min(self.time_map, key=lambda x:abs(x-self.t_min))
      t_max_m = min(self.time_map, key=lambda x:abs(x-self.t_max))

      f_min_i = np.where(self.freq_map == f_min_m)[0][0]
      f_max_i = np.where(self.freq_map == f_max_m)[0][0]
      t_min_i = np.where(self.time_map == t_min_m)[0][0]
      t_max_i = np.where(self.time_map == t_max_m)[0][0]

      sygAxes = plt.axes([0.05, 0.05, 0.8, 0.1])  
      tfAxes = plt.axes([0.05, 0.15, 0.8, 0.8])
      sygAxes.plot(self.time[t_min_i : t_max_i],self.signal[self.channel][t_min_i : t_max_i])
      plt.xlim((t_min_m, t_max_m))
      tfAxes.imshow(self.power[f_min_i:f_max_i, t_min_i:t_max_i],aspect='auto',origin='lower',interpolation='nearest',   
                  extent=(t_min_m-dt/2,t_max_m+dt/2,f_min_m-df/2,f_max_m+df/2))  
      plt.setp(tfAxes,xticklabels=[])
      plt.title(self.title)
      plt.show()