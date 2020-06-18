# -*- coding: utf-8 -*-

import pyedflib
import numpy as np
import scipy.signal as ss
import matplotlib.pyplot as plt
import re
import matplotlib.gridspec as gridspec



class Fourier(object):
    def __init__(self, *, filename, Fs, channels, window, reference1, 
                 reference2 = None, overlap = 0, f_min = None, f_max = None, t_min = None, 
                 t_max = None): 
        
        self.__filename = filename
        self.__Fs = Fs
        self.__reference1 = reference1
        self.__reference2 = reference2
        self.__channels = channels
        self.__window = window
        self.__overlap = overlap
        self.__f_min = f_min
        self.__f_max = f_max
        self.__t_min = t_min
        self.__t_max = t_max
        
        
        
        self.__read_from_edf()
        
        self.__montage()
        
        self.__time_freq()
        
        if self.__t_min == None:
            self.__t_min = self.__time_map[0]
            
        if self.__t_max == None:
            self.__t_max = self.__time_map[-1]
        
        if self.__f_min == None:
            self.__f_min = self.__freq_map[0]
            
        if self.__f_max == None:
            self.__f_max = self.__freq_map[-1]
        
            
        self.__TFRPlot()
     
      

    
    @property
    def filename(self):
        return self.__filename
    
    @property
    def Fs(self):
        return self.__Fs

    @property
    def reference1(self):
        return self.__reference1

    @property
    def reference2(self):
        return self.__reference2

    @property
    def channels(self):
        return self.__channels

    @property
    def window(self):
        return self.__window

    @property
    def overlap(self):
        return self.__overlap

    @property
    def f_min(self):
        return self.__f_min

    @property
    def f_max(self):
        return self.__f_max

    @property
    def t_min(self):
        return self.__t_min

    @property
    def t_max(self):
        return self.__t_max

    

    def __read_from_edf(self): 
  
        print('Reading the data from edf file.')
        f = pyedflib.EdfReader(self.__filename)
        Fs = self.__Fs
        n = f.signals_in_file
        signal_label = f.getSignalLabels()
        self.__signal = np.zeros((n, f.getNSamples()[0]))
        self.__signal_labels = []
        for i in np.arange(n):
            self.__signal[i, :] = f.readSignal(i)
            self.__signal_labels.append(re.sub(r'\W','',str(signal_label[i])))
        self.__time = np.arange(0, np.shape(self.__signal)[1]/Fs, 1/Fs)
        f.close()

    
    
    @property
    def time(self):
        return self.__time
    
    @property
    def signal_labels(self):
        return self.__signal_labels


    def __montage(self):
        
        b, a = ss.butter(2, 0.03, btype = 'highpass')
   
        if self.__reference2 == None:
                
            if isinstance(self.__reference1, int):
                a1 = self.__reference1
            if isinstance(self.__reference1, str):
                a1 = self.__signal_labels.index(self.__reference1)
                    
            s1 = self.__signal[a1]

            for i in range(np.shape(self.__signal)[0]):
                self.__signal[i] -= s1
                self.__signal[i] = ss.filtfilt(b, a, self.__signal[i])
  
        else:
                
            if isinstance(self.__reference1, int) & isinstance(self.__reference2, int):
                a1 = self.__reference1
                a2 = self.__reference2
                
            if isinstance(self.__reference1, str) & isinstance(self.__reference2, str):
                a1 = self.__signal_labels.index(self.__reference1)
                a2 = self.__signal_labels.index(self.__reference2)
                    
            s1 = self.__signal[a1]
            s2 = self.__signal[a2]

            for i in range(np.shape(self.signal)[0]):
                self.__signal[i] -= 0.5*(s1+s2)
                self.__signal[i] = ss.filtfilt(b, a, self.__signal[i])
   
        
    @property
    def signal(self):
        return self.__signal
    
   
    def __time_freq(self):
        
        Nx = self.__signal.shape[1]
        self.__No = len(self.__window)
        self.__window = self.__window/np.linalg.norm(self.__window)
        
        if self.__overlap != 0:
            self.__window_pos = np.arange(0, Nx, self.__overlap)

        else:
            self.__window_pos = np.arange(0, Nx, self.__No)
                        
        self.__time_map = self.__window_pos/self.__Fs
          
        self.__freq_map = np.fft.rfftfreq(self.__No, 1/self.__Fs)
        self.__z = np.zeros(int(self.__No/2))       #half of window to add to the begining and to the end 
        
        
        

    def __spectrogram(self, channel):
        
        
        if isinstance(channel, int):
            self.__x = self.__signal[channel]
            self.__channel_name = self.__signal_labels[channel]
                
        if isinstance(channel, str):
            self.__x = self.__signal[self.__signal_labels.index(channel)]
            self.__channel_name = channel

        N_windows = len(self.__window_pos)                     #numbers of windows
        self.__power = np.zeros((len(self.__freq_map),N_windows))              
        sig = np.concatenate((self.__z,self.__x,self.__z))
        for i,pos in enumerate(self.__window_pos):
            s = sig[pos:pos+self.__No] #part of the signal with len of the window
            s = s*self.__window    #convolution
            S = np.fft.rfft(s)  
            Power_tmp = S*S.conj()    #power spectrum = S*S conjuction
            Power_tmp = Power_tmp.real/self.__Fs    #The imaginary part is 0
            if len(s)%2 ==0:        #add the negative part of the spectrum
                Power_tmp[1:-1] *=2
            else:
                Power_tmp[1:] *=2 
            self.__power[:,i] = Power_tmp
            
        return self.__x, self.__power, self.__channel_name
            

    
    def __TFRPlot(self):
        
    
      
        df = self.__freq_map[1]-self.__freq_map[0]
        dt = self.__time_map[1]-self.__time_map[0]

        f_min_m = min(self.__freq_map, key=lambda x:abs(x-self.__f_min))
        f_max_m = min(self.__freq_map, key=lambda x:abs(x-self.__f_max))
        t_min_m = min(self.__time_map, key=lambda x:abs(x-self.__t_min))
        t_max_m = min(self.__time_map, key=lambda x:abs(x-self.__t_max))

        f_min_i = np.where(self.__freq_map == f_min_m)[0][0]
        f_max_i = np.where(self.__freq_map == f_max_m)[0][0]
        t_min_i = np.where(self.__time_map == t_min_m)[0][0]
        t_max_i = np.where(self.__time_map == t_max_m)[0][0]
        
        
        
        n = len(self.__channels)
        
        if n == 1:
            k = 1
            m = 1
        elif n == 2:
            k = 1
            m = 2
        else:
            k = n//2
            m = k
       
        
        fig = plt.figure(figsize=(10, 8))
        outer = gridspec.GridSpec(k, m, wspace=0.15*k, hspace=0.15*k)

        for i in range(n):
            inner = gridspec.GridSpecFromSubplotSpec(2, 1, subplot_spec=outer[i],
                                            hspace=0, height_ratios=[8,1])
            
           
            x, power, name = self.__spectrogram(self.__channels[i])
        
            tfAxes = plt.Subplot(fig, inner[0,0])
            tfAxes.imshow(power[f_min_i:f_max_i, t_min_i:t_max_i],aspect='auto',
                          origin='lower',interpolation='nearest',   
                          extent=(t_min_m-dt/2,t_max_m+dt/2,f_min_m-df/2,f_max_m+df/2))  
            plt.setp(tfAxes,xticklabels=[], ylabel = 'Frequency [Hz]', 
                     title = 'Channel ' + name)
            
            sygAxes = plt.Subplot(fig, inner[1,0])
            sygAxes.plot(self.__time,x)
            plt.setp(sygAxes, xlim = (t_min_m, t_max_m), xlabel = 'Time [s]')
            
            fig.add_subplot(tfAxes)
            fig.add_subplot(sygAxes)
       
        plt.show()
        