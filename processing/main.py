#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Nov 18 14:32:47 2017

@author: alexmacbook
"""

import numpy as np
import scipy as sp
import matplotlib.pyplot as plt, IPython.display as ipd
import librosa, librosa.display
import random
import os

CHANNELS = 1
BYTES_PER_SAMPLE = 2
SR = 44100
PAD_DURATION = 0.500

##SOUND STANDARDIZATION
STD_PITCH = 55 #G3
BPM = 100.0 #100bpm

##FOLDERS
PRE_AUDIO = "pre_audio"
POST_SOUNDS = "post_sounds"
POST_SNARE = "post_percussion"


def concatenate_segments(x, onset_samples, pad_duration=0.500):
    silence = np.zeros(int(pad_duration*sr)) # silence
    frame_sz = min(np.diff(onset_samples))   # every segment has uniform frame size
    i = 0
    len_onsets = len(onset_samples)
    tone = []
    while(((onset_samples[i+1])<20000) or (i < 1)):
        z = x[onset_samples[i]:onset_samples[i+1]]
        tone = np.concatenate([tone, z])
        i = i+1
    return tone
    
def concatenate_segments_snare(x, onset_samples, pad_duration=0.500):
    """Concatenate segments into one signal."""
    silence = numpy.zeros(int(pad_duration*SR)) # silence
    frame_sz = min(np.diff(onset_samples))   # every segment has uniform frame size
    return np.concatenate([
        np.concatenate([x[i:i+frame_sz], silence]) # pad segment with silence
        for i in onset_samples
    ])

def speed_adjust(x_pre, sr):
    onset_env = librosa.onset.onset_strength(x_pre, sr=sr)
    tempo = librosa.beat.tempo(onset_envelope=onset_env, sr=sr)
    x_fast = librosa.effects.time_stretch(x_pre, BPM / tempo)
    return x_fast
    
def extract_sound(path, song_name):
    print(path)
    x_pre, sr = librosa.load(path, sr=SR)
    x_pre = x_pre[0:1000000]
    x_fast = speed_adjust(x_pre, sr)
    
    x = x_fast[0:200000]
    onset_frames = librosa.onset.onset_detect(x, sr=sr,  backtrack=True, hop_length=512)
    onset_samples = librosa.frames_to_samples(onset_frames)
    #onset_times = librosa.frames_to_time(onset_frames, sr=sr)
    #clicks = librosa.clicks(times=onset_times, length=len(x))
    concatenated_signal = concatenate_segments(x, onset_samples, 0.500)
    
    y = concatenated_signal
    pitches, magnitudes = librosa.piptrack(y, sr=sr)
    pitches = pitches[magnitudes > np.median(magnitudes)]
    pitches = [int(a) for (a) in pitches]
    pitch = int(librosa.hz_to_midi(sp.stats.mode(pitches)[0]))
    pitched_y = librosa.effects.pitch_shift(y, sr, n_steps=STD_PITCH-pitch)
    librosa.output.write_wav(POST_SOUNDS+'/'+song_name, pitched_y, sr)
        
    

def extract_features(x):
    if(len(x) > 0):
        energy = sp.linalg.norm(x)
    else:
         energy = 0
    return energy
        
def extract_snare(path, song_name):
    x, sr = librosa.load(path, sr=SR)
    main_struct_frame = int(sr*(60/(BPM/8)))
    max_frame_energy = 0
    found_i = 0
    for i in range(0, int((len(x) / main_struct_frame))):
        frame = i*main_struct_frame
        #frame_energy = librosa.feature.rmse(y=x[frame:frame+main_struct_frame])
        #frame_energy = np.max(frame_energy[0])
        frame_energy = extract_features(x[frame:frame+main_struct_frame])
        if (frame_energy > max_frame_energy):
            found_i = i
            max_frame_energy = frame_energy
            print(found_i)
        
    #x = speed_adjust(x, sr)
    
    x = x[(found_i*main_struct_frame):((found_i+1)*main_struct_frame)]
    print(len(x[(found_i*main_struct_frame):((found_i+1)*main_struct_frame)]))

    X = librosa.stft(x)
    H, P = librosa.decompose.hpss(X, power=3.0, margin=(1,2))
    #h = librosa.istft(H)
    p = librosa.istft(P)

    onset_frames = librosa.onset.onset_detect(p, sr=sr, delta=0.04, wait=4)
    #onset_times = librosa.frames_to_time(onset_frames, sr=sr)
    onset_samples = librosa.frames_to_samples(onset_frames)
    
    frame_sz = int(SR*0.090)
    f_energy = np.array([extract_features(p[i:i+frame_sz]) for i in onset_samples])

    median_energy = np.median(f_energy)
    print(f_energy)
    silence = np.zeros(int(PAD_DURATION*SR)) #silence
    frame_sz = min(np.diff(onset_samples))   #every segment has uniform frame size
    for i, onset in enumerate(onset_samples):
        if (f_energy[i] > median_energy):
            sample = np.concatenate([p[onset:onset+frame_sz], silence]) # pad segment with silence
            librosa.output.write_wav(POST_SNARE+'/'+song_name+'_'+str(f_energy[i])+'_'+str(i)+".wav", sample, SR)

        
def main():
    print("Main")
    main_dir = os.getcwd()+'/'+PRE_AUDIO
    for subdir, dirs, files in os.walk(main_dir):
        for i, file in enumerate(files):
            if i > 0:
                path = os.path.join(subdir, file)
                print(path)
                extract_snare(path,file)
                #extract_sound(path, file)
    
main()
    
