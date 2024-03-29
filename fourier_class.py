# -*- coding: utf-8 -*-

import pyedflib
import numpy as np
import scipy.signal as ss
import matplotlib.pyplot as plt
import re
import matplotlib.gridspec as gridspec
import math

class WrongChannel(Exception):
    pass

class Fourier(object):
    def __init__(self, *, filename, Fs, channels, window, reference1, 
                 reference2 = None, overlap = 0, f_min = None, f_max = None, t_min = None, 
                 t_max = None): 
        """
        Parameters
        ----------
      
        filename : str
            edf filename with EEG data
            
        Fs : int
            sampling rate in Hz
            
        channels : list of int or str
           a list of channels for which time-frequency map will be shown
            
        window : ndarray
            a window with its length which is convolved with the signal 
            (for more info see https://numpy.org/doc/stable/reference/routines.window.html
        
        reference1 : int or str
            a channel which is treated as reference; reference channel is 
            subtracted from all others channels: if one given -> -reference1;
        
        reference2 : int or str, optional
            a channel which is treated as reference; references channels are subtracted from all
            other channels: if two given -> -0.5*(reference1+reference2). The default is None.
        
        overlap : int, optional
            number of samples between the beginnings of the window -> 
            length of the overlapping vector is equal to the length of the window 
            minus overlap; if overlap = 0 -> space between windows = len(window)
            (no overlapping). The default is 0.
        
        f_min : it or float, optional
            approximate minimum value of the frequency
            presented the time-frequency map; from 0 to around Fs/2;
            for more info see https://numpy.org/doc/stable/reference/generated/numpy.fft.rfftfreq.html
            The default is 0.
        
        f_max : int or float, optional
            approximate maximum value of the frequency presented on the
            on a time-frequency map; from 0 to around Fs/2;
            for more info see https://numpy.org/doc/stable/reference/generated/numpy.fft.rfftfreq.html 
            The default is around Fs/2.
        
        t_min : int or float, optional
            approximate minimum value of the time presented on the
            time-frequency map; from 0 to a signal length is sec = signal_lenght/Fs;
            The default is 0.
        
        t_max : int or float, optional
            approximate maximum value of the time preseted on the
            time-frequency map; from 0 to signal length is sec = signal_lenght/Fs; 
            The default is signal_lenght/Fs.

       """
       
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
        
        chan_lab =  all(item in self.__signal_labels for item in self.__channels)
        chan_num = all(item in self.__signal_numbers for item in self.__channels)
        
    
        if (chan_lab == False) & (chan_num == False):
            
            raise WrongChannel("Wrong Channel list -> list must contain only "
                               "numbers or only labels -> labels of channels: ",
                               self.__signal_labels," -> numbers of channels: ",
                               self.__signal_numbers)
        
        if (self.__reference1 not in self.__signal_labels) & (self.__reference1 not in self.__signal_numbers):
        
            raise WrongChannel("Wrong Reference1 -> labels of channels: ", self.__signal_labels,
                               " -> numbers of channels: ", self.__signal_numbers)
        
        
        if (self.__reference2 != None) & (self.__reference2 not in self.__signal_labels) & (self.__reference2 not in self.__signal_numbers):
        
            raise WrongChannel("Wrong Reference2 -> None -> labels of channels: ", self.__signal_labels,
                               " -> numbers of channels: ", self.__signal_numbers)
        
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
        """
        Returns
        -------
        string
            path to the file
        """
        return self.__filename
    
    @property
    def Fs(self):
        """
        Returns
        -------
        int
            sampling rate
        """
        return self.__Fs

    @property
    def reference1(self):
        """
        Returns
        -------
        int or str
            label or number of channel
        """
        return self.__reference1

    @property
    def reference2(self):
        """
        Returns
        -------
        int or str
            label or number of channel
        """
        return self.__reference2

    @property
    def channels(self):
        """
        Returns
        -------
        list of int or str
            list of labels or numbers of choosen channel
        """
        return self.__channels

    @property
    def window(self):
        """
        Returns
        -------
        ndarray
            a window with its length which is convolved with the signal
        """
        return self.__window

    @property
    def overlap(self):
        """
        Returns
        -------
        int
            number of samples between the beginnings of the window; if 0 -> no overlappig
        """
        return self.__overlap

    @property
    def f_min(self):
        """
        Returns
        -------
        int or float
            approximate minimum value of the frequency
            presented the time-frequency map
        """
        return self.__f_min

    @property
    def f_max(self):
        """
        Returns
        -------
        int or float
            approximate maximum value of the frequency
            presented the time-frequency map
        """
        return self.__f_max

    @property
    def t_min(self):
        """
        Returns
        -------
        int or float
            approximate minimum value of the time
            presented the time-frequency map
        """
        return self.__t_min

    @property
    def t_max(self):
        """
        Returns
        -------
        int or float
            approximate maximum value of the time
            presented the time-frequency map
        """
        return self.__t_max

    def __read_from_edf(self): 

        print('Reading the data from edf file.')
        f = pyedflib.EdfReader(self.__filename)
        Fs = self.__Fs
        n = f.signals_in_file
        self.__signal_numbers = np.arange(n).tolist()
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
        """
        Returns
        -------
        array
            vector of time samples
        """
        return self.__time
    
    @property
    def signal_labels(self):
        """
        Returns
        -------
        list of str
            list of channels labels
        """
        return self.__signal_labels
    
    @property
    def signal_numbers(self):
        """
        Returns
        -------
        list of int
            list of channels numbers
        """
        return self.__signal_numbers


    def __montage(self):
        
        b, a = ss.butter(2, 0.03, btype = 'highpass')  #removes low frequencies
   
        if self.__reference2 == None:
                
            if isinstance(self.__reference1, int):
                a1 = self.__reference1
            if isinstance(self.__reference1, str):
                a1 = self.__signal_labels.index(self.__reference1)
                    
            s1 = self.__signal[a1]
            
            self.__signal -= s1

            for i in range(np.shape(self.__signal)[0]):
                self.__signal[i] = ss.filtfilt(b, a, self.__signal[i])
  
        else:
                
            if isinstance(self.__reference1, int):
                a1 = self.__reference1
                
            if isinstance(self.__reference2, int):
                a2 = self.__reference2
                
            if isinstance(self.__reference1, str):
                a1 = self.__signal_labels.index(self.__reference1)
            
            if isinstance(self.__reference2, str):
                a2 = self.__signal_labels.index(self.__reference2)
                    
            s1 = self.__signal[a1]
            s2 = self.__signal[a2]
            
            self.__signal -= 0.5*(s1+s2)

            for i in range(np.shape(self.signal)[0]):
                self.__signal[i] = ss.filtfilt(b, a, self.__signal[i])
   
        
    @property
    def signal(self):
        """
        Returns
        -------
        ndarray
            matrix with signal after montage and filtration
        """
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

        f_min_m = min(self.__freq_map, key=lambda x:abs(x-self.__f_min))   #real f_min value
        f_max_m = min(self.__freq_map, key=lambda x:abs(x-self.__f_max))
        t_min_m = min(self.__time_map, key=lambda x:abs(x-self.__t_min))
        t_max_m = min(self.__time_map, key=lambda x:abs(x-self.__t_max))

        f_min_i = np.where(self.__freq_map == f_min_m)[0][0]  #index of f_min value
        f_max_i = np.where(self.__freq_map == f_max_m)[0][0]
        t_min_i = np.where(self.__time_map == t_min_m)[0][0]
        t_max_i = np.where(self.__time_map == t_max_m)[0][0]

        number_of_plots = len(self.__channels)

        number_of_rows = round(math.sqrt(number_of_plots))
        number_of_columns = number_of_plots // number_of_rows

        if number_of_rows * number_of_columns < number_of_plots:
            number_of_columns += 1

        fig = plt.figure(figsize=(10, 8))
        outer = gridspec.GridSpec(number_of_rows, number_of_columns, wspace=0.15* number_of_rows,
                                  hspace=0.15* number_of_rows)

        for i in range(number_of_plots):
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
            plt.setp(sygAxes, xlim = (t_min_m-dt/2, t_max_m+dt/2), xlabel = 'Time [s]')
            
            fig.add_subplot(tfAxes)
            fig.add_subplot(sygAxes)
       
        plt.show()
        