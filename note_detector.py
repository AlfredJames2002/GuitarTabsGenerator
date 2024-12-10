import numpy as np
import soundfile as sf
import librosa
import os
from scipy.signal import butter, filtfilt

# Bandpass filter function
def bandpass_filter(data, lowcut, highcut, fs, order=5):
    nyquist = 0.5 * fs #highest freq that can be sampled
    low = lowcut / nyquist
    high = highcut / nyquist
    #normalize so it is from 0 to 1
    b, a = butter(order, [low, high], btype='band')
    filtered_data = filtfilt(b, a, data)
    return filtered_data

# Frequency ranges for each string (open to around 12th fret in standard tuning)
string_ranges = [
    (82.41, 330.0),  # Low E
    (110.0, 440.0),  # A
    (146.83, 587.33),  # D
    (196.0, 784.0),  # G
    (246.94, 987.77),  # B
    (329.63, 1319.0)   # High E
]

# Function to check if pitch is within any guitar string's range
def is_valid_guitar_pitch(pitch):
    for low, high in string_ranges:
        if low <= pitch <= high:
            return True
    return False

def load_song(filepath):
    y, sr = librosa.load(filepath, sr=44100)
    filtered_y = bandpass_filter(y, lowcut=80.0, highcut=4000.0, fs=sr)
    
    # Pitch and onset detection
    pitches, magnitudes = librosa.piptrack(y=filtered_y, sr=sr)
    onset_frames = librosa.onset.onset_detect(y=filtered_y, sr=sr)
    onset_times = librosa.frames_to_time(onset_frames, sr=sr)

    note_values = []
    for onset_frame in onset_frames:
        # Find all significant pitches (above a certain magnitude threshold)
        threshold = np.median(magnitudes[:, onset_frame])
        pitches_at_frame = pitches[:, onset_frame]
        magnitudes_at_frame = magnitudes[:, onset_frame]
    
        detected_pitches = []
        for i, magnitude in enumerate(magnitudes_at_frame):
            if magnitude > threshold and pitches_at_frame[i] > 0:
                pitch = pitches_at_frame[i]
                if is_valid_guitar_pitch(pitch):
                    detected_pitches.append((pitch, magnitude))
    
        detected_pitches = sorted(detected_pitches, key=lambda x: x[1], reverse=True)[:6]
    
        for pitch, mag in detected_pitches:
            onset_time = librosa.frames_to_time(onset_frame, sr=sr)
            note = librosa.hz_to_note(pitch)
            note_values.append((note, onset_time, pitch))

    return np.array(note_values)  # Return as a NumPy array


