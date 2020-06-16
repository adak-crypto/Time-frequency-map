### Time-frequency-map

The code makes time-frequency map using Fourier Transform

<ul>
  <li><b>os.chdir</b> - path to the data folder </li>
<li><b>filename</b> - edf filename with EEG data</li>
<li><b>Fs</b> - sampling in Hz (int)</li>
<li><b>window</b> - a window with its length which is convolved with signal (for more info see https://numpy.org/doc/stable/reference/routines.window.html)</li>
<li><b>channel</b> - channel for which time-frequency map will be shown (label of channel str or number of channel int)</li>
<li><b>overlap</b> - number of samples between beginnings of the window -> samples which will overlap are equal to the length of the window minus overlap; default to 0 (int)</li>
<li><b>f_min, f_max</b> - approximate values of minimum and maximum frequencies which will be shown on time-frequency map; from 0 to around Fs/2; for more info see https://numpy.org/doc/stable/reference/generated/numpy.fft.rfftfreq.html; f_min default to 0; f_max default to around Fs/2 (int or float)</li>
<li><b>t_min, t_max</b> - approximate values of minimum and maximum time which will be shown on time-frequency map; from 0 to signal length is sec = signal_lenght/Fs; t_min default to 0; t_max default to signal_leght/Fs (int or float)</li>
<li><b>title</b> - title of the chart; default to 'Channel [channel_number]' (str)</li>
<li><b>reference1, reference2</b> - channels which are treated as references; reference2 defaults to None; reference channels are subtracted from all others channels: if one given -> -0.5*reference1; if two given -> -0.5*(reference1+reference2) (label of channel str or number of channel int)</li>
  </ul>
