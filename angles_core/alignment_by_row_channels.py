from __future__ import absolute_import, division, print_function, unicode_literals

import math
from collections import defaultdict
from subprocess import call
import os.path
import numpy as np
import scipy.io.wavfile
from scipy import signal
from angles_core import url_redirect as redirect

# Extract audio from video file, save as wav audio file
# INPUT: Video file
# OUTPUT: Does not return any values, but saves audio as wav file

def extract_audio(dir_, video_file):
    track_name = video_file.split(".")
    audio_output = track_name[0] + "WAV.wav"  # !! CHECK TO SEE IF FILE IS IN UPLOADS DIRECTORY
    output = dir_ + audio_output
    call(["ffmpeg", "-y", "-i", dir_ + video_file, "-vn", "-ac", "1", "-f", "wav", output])
    return output

# Read file
# INPUT: Audio file
# OUTPUT: Sets sample rate of wav file, Returns data read from wav file (numpy array of integers)

def read_audio(audio_file):
    rate, data = scipy.io.wavfile.read(audio_file)  # Return the sample rate (in samples/sec) and data from a WAV file
    return data, rate


def make_horiz_bins(data, fft_bin_size, overlap, box_height):
    horiz_bins = defaultdict(list)
    # process first sample and set matrix height
    sample_data = data[0:fft_bin_size]  # get data for first sample
    if len(sample_data) == fft_bin_size:  # if there are enough audio points left to create a full fft bin
        intensities = fourier(sample_data)  # intensities is list of fft results
        for i, intensity in enumerate(intensities):
            box_y = i // box_height
            horiz_bins[box_y].append((intensity, 0, i))  # (intensity, x, y)
    # process remainder of samples
    x_coord_counter = 1  # starting at second sample, with x index 1
    for i in range(int(fft_bin_size - overlap), len(data), int(fft_bin_size - overlap)):
        sample_data = data[i:i + fft_bin_size]
        if len(sample_data) == fft_bin_size:
            intensities = fourier(sample_data)
            for j, intensity in enumerate(intensities):
                box_y = j // box_height
                horiz_bins[box_y].append((intensity, x_coord_counter, j))  # (intensity, x, y)
        x_coord_counter += 1

    return horiz_bins


# Compute the one-dimensional discrete Fourier Transform
# INPUT: list with length of number of samples per second
# OUTPUT: list of real values len of num samples per second
def fourier(sample):  # , overlap):
    mag = []
    fft_data = np.fft.fft(sample)  # Returns real and complex value pairs
    for i in range(len(fft_data) // 2):
        r = fft_data[i].real ** 2
        j = fft_data[i].imag ** 2
        mag.append(round(math.sqrt(r + j), 2))

    return mag


def make_vert_bins(horiz_bins, box_width):
    boxes = defaultdict(list)
    for key in horiz_bins:
        for bin_ in horiz_bins[key]:
            box_x = bin_[1] // box_width
            boxes[(box_x, key)].append(bin_)
            
    return boxes


def find_bin_max(boxes, maxes_per_box):
    freqs_dict = defaultdict(list)
    for key in boxes:
        max_intensities = [(1, 2, 3)]
        for box in boxes[key]:
            if box[0] > min(max_intensities)[0]:
                if len(max_intensities) < maxes_per_box:  # add if < number of points per box
                    max_intensities.append(box)
                else:  # else add new number and remove min
                    max_intensities.append(box)
                    max_intensities.remove(min(max_intensities))
        for max_intensity in max_intensities:
            freqs_dict[max_intensity[2]].append(max_intensity[1])
    return freqs_dict


def find_freq_pairs(freqs_dict_orig, freqs_dict_sample):
    return [(t1, t2)
            for key in freqs_dict_sample
            if key in freqs_dict_orig
            for t1 in freqs_dict_sample[key]
            for t2 in freqs_dict_orig[key]]


def find_delay(time_pairs):
    t_diffs = defaultdict(int)
    for t1, t2 in time_pairs:
        t_diffs[t1 - t2] += 1    
    t_diffs_sorted = sorted(t_diffs.items(), key=lambda x: x[1])
    #print(t_diffs_sorted)
    time_delay = t_diffs_sorted[-1][0]

    return time_delay


# Find time delay between two video files
def align(video1, video2, dir_, fft_bin_size=1024, overlap=0, box_height=512, box_width=43, samples_per_box=7):
    
    # Process first file
    wav_file1 = dir_ + video1.split(".")[0] + "WAV.wav"  # !! CHECK TO SEE IF FILE IS IN UPLOADS DIRECTORY
    if not(os.path.exists(wav_file1)):
        wav_file1 = extract_audio(dir_, video1)
        print("Audio Extracted")
    else:
        print("Audio Already Extracted")
    raw_audio1, rate1 = read_audio(wav_file1)

    bins_dict1 = make_horiz_bins(raw_audio1, fft_bin_size, overlap, box_height)  # bins, overlap, box height
    boxes1 = make_vert_bins(bins_dict1, box_width)  # box width
    ft_dict1 = find_bin_max(boxes1, samples_per_box)  # samples per box



    # Process second file
    wav_file2 = dir_ + video2.split(".")[0] + "WAV.wav"  # !! CHECK TO SEE IF FILE IS IN UPLOADS DIRECTORY
    if not(os.path.exists(wav_file2)):
        wav_file2 = extract_audio(dir_, video2)
        print("Audio Extracted")
    else:
        print("Audio Already Extracted")
    raw_audio2, rate2 = read_audio(wav_file2)

    if rate1 == rate2:
        rate = rate1
    else:  # resampling
        secs = len(raw_audio2) // rate2
        new_sample_count = secs * rate1
        raw_audio2 = signal.resample(raw_audio2, new_sample_count)

        rate = rate1
    #print(rate)

    #print("Transforming Data")
    bins_dict2 = make_horiz_bins(raw_audio2, fft_bin_size, overlap, box_height)
    boxes2 = make_vert_bins(bins_dict2, box_width)
    ft_dict2 = find_bin_max(boxes2, samples_per_box)

    print("Finding Time Delay")
    # Determine time delay
    pairs = find_freq_pairs(ft_dict1, ft_dict2)
    delay = find_delay(pairs)
    #print(delay)
    samples_per_sec = rate / fft_bin_size
    seconds = round(delay / samples_per_sec, 4)

    print("Delay Pair: ")
    print(0,str(abs(seconds)))
    return(redirect.url_redirect(seconds, video1[-11:], video2[-11:]))

   # if seconds > 0:
   #     print("Delay Pair: ")
   #     print(0,seconds)
   #     return "https://viewsync.net/watch?v="+video1[-11:]+"&t=0"+"&v="+video2[-11:]+"&t="+str(seconds)+"&mode=solo"
        
   # else:
   #     print("Delay Pair: ")
   #     print(abs(seconds),0)
   #    return "https://viewsync.net/watch?v="+video1[-11:]+"&t="+str(abs(seconds))+"&v="+video2[-11:]+"&t=0"+"&mode=solo"
        

