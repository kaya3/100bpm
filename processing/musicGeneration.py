#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Nov 18 14:32:47 2017

@author: alexmacbook
"""

import numpy as np
import scipy as sp
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
POST_SNARE = "post_percussion2"


def reverb(x, sr):
    # Initialize output array
    output = np.zeros(x.shape)
    
    # Initialize filter coefficients
    a = np.array([0.6, 0.4, 0.2, 0.1, 0.7, 0.6, 0.8])
    R = np.array([700, 900, 600, 400, 450, 390])
    
    # Implement reverb algorithm
    num1 = np.append(0, np.zeros(R[0]-1)); num1 = np.append(num1, 1);
    den1 = np.append(1, np.zeros(R[0]-1)); den1 = np.append(den1, -a[0]);
    d1 = sp.signal.lfilter(num1, den1, x)
    num2 = np.append(0, np.zeros(R[1]-1)); num2 = np.append(num2, 1);
    den2 = np.append(1, np.zeros(R[1]-1)); den2 = np.append(den2, -a[1]);
    d2 = sp.signal.lfilter(num2, den2, x)
    num3 = np.append(0, np.zeros(R[2]-1)); num3 = np.append(num3, 1);
    den3 = np.append(1, np.zeros(R[2]-1)); den3 = np.append(den3, -a[2]);
    d3 = sp.signal.lfilter(num3, den3, x)
    num4 = np.append(0, np.zeros(R[3]-1)); num4 = np.append(num4, 1);
    den4 = np.append(1, np.zeros(R[3]-1)); den4 = np.append(den4, -a[3]);
    d4 = sp.signal.lfilter(num4, den4, x)
    d = d1 + d2 + d3 + d4
    num5 = np.append(a[4], np.zeros(R[4]-1)); num5 = np.append(num5, 1);
    den5 = np.append(1, np.zeros(R[4]-1)); den5 = np.append(den5, a[4]);
    d = sp.signal.lfilter(num5, den5, d)
    num6 = np.append(a[5], np.zeros(R[5]-1)); num6 = np.append(num6, 1);
    den6 = np.append(1, np.zeros(R[5]-1)); den6 = np.append(den6, a[5]);
    d = sp.signal.lfilter(num6, den6, d)
    output = x + a[6]*d;
    # Clip amplitude to minimize distortion
    output *= 0.35
    
    # Ensure correct output array size
    #output.shape=np.original.shape
    
    return output

def speed_adjust(x_pre, sr):
    onset_env = librosa.onset.onset_strength(x_pre, sr=sr)
    tempo = librosa.beat.tempo(onset_envelope=onset_env, sr=sr)
    x_fast = librosa.effects.time_stretch(x_pre, tempo / BPM)
    return x_fast
    
    
def get_pitch(y, sr):
    pitches, magnitudes = librosa.piptrack(y, sr=sr)
    pitches = pitches[magnitudes > np.median(magnitudes)]
    pitches = [int(a) for (a) in pitches]
    pitch = int(librosa.hz_to_midi(sp.stats.mode(pitches)[0]))
    return pitch
    
def extract_sound(path, song_name):

       
        #pitches, magnitudes = librosa.piptrack(y, sr=sr)
        #pitches = pitches[magnitudes > np.median(magnitudes)]
        #pitches = [int(a) for (a) in pitches]
        #pitch = int(librosa.hz_to_midi(sp.stats.mode(pitches)[0]))
        #pitched_y = librosa.effects.pitch_shift(y, SR, n_steps=STD_PITCH-pitch)
        librosa.output.write_wav(POST_SOUNDS+'/'+song_name, y, sr)
        
        
def generate_kicks(path, notes):
    #loading sound file
    y, sr = librosa.load(path, sr=SR)
    
    #defining melody loop boundaries
    beat_length = int(sr*(60/(BPM/8)))
    kick = np.zeros([beat_length])
    sound_length = len(y)
            
    #iterating through the notes
    for n in notes:
        note_wav = np.zeros([beat_length])
        current_sample = int((n/1000) * SR)
        if(current_sample+sound_length <= beat_length):
            note_wav[current_sample:current_sample+sound_length] = y
        else:
            note_wav[current_sample::] = y[:(beat_length - (current_sample+sound_length))]
        kick += note_wav
    return kick
    
def generate_snares(path, notes):
    #loading sound file
    y, sr = librosa.load(path, sr=SR)
    
    #defining melody loop boundaries
    beat_length = int(sr*(60/(BPM/8)))
    snare = np.zeros([beat_length])
    sound_length = len(y)
            
    #iterating through the notes
    for n in notes:
        note_wav = np.zeros([beat_length])
        current_sample = int((n/1000) * SR)
        if(current_sample+sound_length <= beat_length):
            note_wav[current_sample:current_sample+sound_length] = y
        else:
            note_wav[current_sample::] = y[:(beat_length - (current_sample+sound_length))]
        snare += note_wav
    return snare
    
    
def generate_melody(path, notes):    
    #loading sound file
    y, sr = librosa.load(path, sr=SR)
    
    #defining melody loop boundaries
    beat_length = int(sr*(60/(BPM/8)))
    instrumental = np.zeros([beat_length])
    sound_length = len(y)
    
    #get pitch of sample_sound
    sample_pitch = get_pitch(y, sr)
            
    #iterating through the notes
    for i, n in enumerate(notes):
        pitch = n[0]
        raw_sample_pitch = sample_pitch % 12
        raw_pitch = pitch % 12
        if(pitch >= 60):
            raw_pitch = (pitch % 12)+12

        pitched_y = librosa.effects.pitch_shift(y, sr, n_steps=raw_pitch-raw_sample_pitch)
        note_wav = np.zeros([beat_length])
        current_sample = int((n[1]/1000) * SR)
        if(current_sample+sound_length <= beat_length):
            note_wav[current_sample:current_sample+sound_length] = pitched_y
        else:
            note_wav[current_sample::] = pitched_y[:(beat_length - (current_sample+sound_length))]
        instrumental += note_wav
    return instrumental

    
def generate_single_pitches(path):
    #loading sound file
    y, sr = librosa.load(path, sr=SR)
       
    #get pitch of sample_sound
    sample_pitch = get_pitch(y, sr)
            
    #iterating through the notes
    for i in range(48,65):
        pitch = i
        raw_sample_pitch = sample_pitch % 12
        raw_pitch = pitch % 12
        if(pitch >= 60):
            raw_pitch = (pitch % 12)+12
        pitched_y = librosa.effects.pitch_shift(y, sr, n_steps=raw_pitch-raw_sample_pitch)
        songname = path.split("/")[-1]
        librosa.output.write_wav("post_sounds_pitched/"+songname+"_"+str(i)+".wav", pitched_y, SR)

def generate_drumbeat(sound_kick, sound_snare, notes_kick, notes_snare, output_filename):
    kicks = generate_kicks(sound_kick, notes_kick)
    snares = generate_snares(sound_snare, notes_snare)
    audio = kicks + snares
    #audio = audio + (reverbed_audio * 0.3) #Mix reverb
    librosa.output.write_wav(output_filename, audio, SR)

    
def generate_song(sound_melody, sound_kick, sound_snare, notes_melody, notes_kick, notes_snare, output_filename):
    
    instrumental = generate_melody(sound_melody, np.array(notes_melody))
    kicks = generate_kicks(sound_kick, notes_kick)
    snares = generate_snares(sound_snare, notes_snare)
    
    audio =  instrumental + snares + kicks
    reverbed_audio = reverb(audio, SR)
    audio = audio + (reverbed_audio * 0.1) #Mix reverb
    librosa.output.write_wav(output_filename, audio, SR)
    

generate_single_pitches("new_post_sounds/01 Somebody (feat. Jeremih).wav")
"""
#if __name__ == '__main__':
generate_song(
    "new_post_sounds/01 Somebody (feat. Jeremih).wav",
    "post_kicks/65 Touchin, Lovin (feat. Nicki Minaj).wav_20.8808708191_25.wav",
    "post_snares/16 Loin (feat. Dany synthé) [Pilule Violette].wav_9.9791841507_9.wav",
    [[55, 920, 201]],
    [50],
    [20],
    "melody.wav"
)
  """  
