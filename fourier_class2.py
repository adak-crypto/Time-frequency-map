# -*- coding: utf-8 -*-

import pyedflib
import numpy as np
import matplotlib.pyplot as plt
import re
import sys

class WrongChannel(Exception):
    pass

class Fourier(object):
    def __init__(self, *, filename, Fs, channel, window, overlap, f_min, f_max, 
               t_min, t_max, reference1, reference2 = None, title = ''): 
        
        self.__filename = filename
        self.__Fs = Fs
        self.__reference1 = reference1
        self.__reference2 = reference2
        self.__channel = channel
        self.__window = window
        self.__overlap = overlap
        self.__f_min = f_min
        self.__f_max = f_max
        self.__t_min = t_min
        self.__t_max = t_max
        self.__title = title
        
        
        self.__read_from_edf()
        
        if self.__channel not in self.__signal_labels:
        
            raise WrongChannel("WrongChannel")
            
          '''
          @title.setter
          def title(self, title):
             if not isinstance(title, str):
                 raise ValueError('"title" mus be a string value')
                self.__title = title
        
        '''
        
        self.__montage()
        self.__spectrogram()
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
    def channel(self):
        return self.__channel

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

    @property
    def title(self):
        return self.__title    
    
        

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

        #return self.signal, self.time, self.signal_labels
    
    
    @property
    def time(self):
        return self.__time
    
    @property
    def signal_labels(self):
        return self.__signal_labels


    def __montage(self):

        try:

            if self.__reference2 == None:
                
                if isinstance(self.__reference1, int):
                    a1 = self.__reference1
                if isinstance(self.__reference1, str):
                    a1 = self.__signal_labels.index(self.__reference1)
                    
                s1 = self.__signal[a1]

                for i in range(np.shape(self.__signal)[0]):
                    self.__signal[i] -= s1
  
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

        except ValueError:
            print("There is not such channel")
            sys.exit(1)

        #return self.signal
        
    @property
    def signal(self):
        return self.__signal
        

    def __spectrogram(self):
        
        '''

        try:
            
            if isinstance(self.__channel, int):
                x = self.signal[self.__channel]
                
            if isinstance(self.__channel, str):
                x = self.signal_labels.index(self.__channel)
       
        #except WrongChannel as e: #ValueError as err:
            #raise IndexError('There is not such channel ', self.__channel)
            #print("There is not such channel", err)
            #sys.exit(1)
            #raise WrongChannel("Wrong channel")
            #print("Wrong channel", e) 
        
            
        except IndexError as e:
            raise WrongChannel('mój tekst').with_traceback(e.__traceback__)
          
        '''
        
        if isinstance(self.__channel, int):
            self.__x = self.__signal[self.__channel]
                
        if isinstance(self.__channel, str):
            self.__x = self.__signal[self.__signal_labels.index(self.__channel)]

        Nx = len(self.__x)
        No = len(self.__window)
        self.__window = self.__window/np.linalg.norm(self.__window)
        window_pos = np.arange(0, Nx, self.__overlap)                        
        self.__time_map = window_pos/self.__Fs
        N_windows = len(window_pos)                     #numbers of windows  
        self.__freq_map = np.fft.rfftfreq(No, 1/self.__Fs)
        self.__power = np.zeros((len(self.__freq_map),N_windows))
        z = np.zeros(int(No/2))                        #half of window to add to the begining and to the end
        sig = np.concatenate((z,self.__x,z))
        for i,pos in enumerate(window_pos):
            s = sig[pos:pos+No] #part of the signal with len of the window
            s = s*self.__window    #convolution
            S = np.fft.rfft(s)  
            Power_tmp = S*S.conj()    #power spectrum = S*S conjuction
            Power_tmp = Power_tmp.real/self.__Fs    #The imaginary part is 0
            if len(s)%2 ==0: 
                Power_tmp[1:-1] *=2
            else:
                Power_tmp[1:] *=2 
            self.__power[:,i] = Power_tmp
        #return self.time_map, self.freq_map, self.power

    
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

        sygAxes = plt.axes([0.05, 0.05, 0.8, 0.1])  
        tfAxes = plt.axes([0.05, 0.15, 0.8, 0.8])
        sygAxes.plot(self.__time[t_min_i : t_max_i],self.__x[t_min_i : t_max_i])
        plt.xlim((t_min_m, t_max_m))
        tfAxes.imshow(self.__power[f_min_i:f_max_i, t_min_i:t_max_i],aspect='auto',origin='lower',interpolation='nearest',   
                  extent=(t_min_m-dt/2,t_max_m+dt/2,f_min_m-df/2,f_max_m+df/2))  
        plt.setp(tfAxes,xticklabels=[])
        plt.title(self.__title)
        plt.show()