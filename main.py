# -*- coding: utf-8 -*-

from fourier_class import Fourier
import os
import numpy as np

def main():
    
    os.chdir('C:\\Users\\Ada\\Documents\\neuroinformatyka\\VIII semestr\\Metody fizyczne\\files\\S001')
    filename = 'S001R07.edf'
    Fs = 160
    window = np.hamming(100)
    channel = 15
    overlap = len(window)//3
    f_min = 30
    f_max = 60
    t_min = 20
    t_max = 50
    title = 'Channel ' + str(channel)
    reference1 = 'T9'
    reference2 = 'T10'
   
    Fourier(filename = filename, Fs = Fs, channel = channel, window = window,
            overlap = overlap, f_min = f_min, f_max = f_max, t_min = t_min, 
            t_max = t_max, reference1 = reference1, reference2 = reference2, 
            title = title)
        

if __name__ == '__main__':
    main()