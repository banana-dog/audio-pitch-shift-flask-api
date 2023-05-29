import librosa
import soundfile as sf
import numpy as np

def read(fname):
    y1, sr1 = librosa.load(fname)
    return y1, sr1
    
def save(data, fname, sr1):
    sf.write(fname, data, sr1, 'PCM_24')

def pitch_shift(audio, pitches, sr1):
    pitched_audios = []
    for steps in pitches:
        pitched = librosa.effects.pitch_shift(audio, sr=sr1, n_steps=steps)
        pitched_audios.append(pitched)
    return np.average(pitched_audios, axis=0)

if __name__=="__main__":
    new_file_name = "new_sound.wav"
    audio, sr1 = read("jfk.wav")
    pitches = [5, -5]
    result = pitch_shift(audio, pitches, sr1)
    save(result, new_file_name, sr1)