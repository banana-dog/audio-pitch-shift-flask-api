import pyaudio
import wave
import numpy as np

# pitch shiftings framework from "pianoputer" https://github.com/Zulko/pianoputer by Zulko is licensed under https://github.com/Zulko/pianoputer/blob/master/LICENSE.txt 
def _stretch(snd_array, factor, window_size, h):
    """Stretches/shortens a sound, by some factor."""
    phase = np.zeros(window_size)
    hanning_window = np.hanning(window_size)
    result = np.zeros(int(len(snd_array) / factor + window_size))
    for i in np.arange(0, len(snd_array) - (window_size + h), h * factor):
        i = int(i)
        # Two potentially overlapping subarrays
        a1 = snd_array[i : i + window_size]
        a2 = snd_array[i + h : i + window_size + h]

        # The spectra of these arrays
        s1 = np.fft.fft(hanning_window * a1)
        s2 = np.fft.fft(hanning_window * a2)

        # Rephase all frequencies
        phase = (phase + np.angle(s2 / s1)) % 2 * np.pi

        a2_rephased = np.fft.ifft(np.abs(s2) * np.exp(1j * phase))
        i2 = int(i / factor)
        result[i2 : i2 + window_size] += hanning_window * a2_rephased.real
    return result.astype("int16")


def _speedx(sound_array, factor):
    """Multiplies the sound's speed by some `factor`"""
    indices = np.round(np.arange(0, len(sound_array), factor))
    indices = indices[indices < len(sound_array)].astype(int)
    return sound_array[indices]


def pitch_shift(snd_array, n, window_size=2**13, h=2**11):
    """Changes the pitch of a sound by ``n`` semitones."""
    factor = 2 ** (1.0 * n / 12.0)
    stretched = _stretch(snd_array, 1.0 / factor, window_size, h)
    return _speedx(stretched[window_size:], factor)


def high_pass(data, proportion=0.75):
    f = np.fft.fft(data)
    f[: int(data.shape[0] * proportion)] = 0
    return np.fft.ifft(f)

FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100
CHUNK = 204800  # work with one huge chunk
audio = pyaudio.PyAudio()


def play_audio(audio):
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, channels=CHANNELS, rate=RATE, output=True)
    sound = audio.astype(np.int16).tostring()
    stream.write(sound)

    stream.stop_stream()
    stream.close()
    p.terminate()


def read_file(fname="file.wav"):
    # https://stackoverflow.com/a/71042208
    with wave.open(fname) as f:
        buffer = f.readframes(f.getnframes())
        # Convert the buffer to a numpy array by checking the size of the sample
        # with in bytes. The output will be a 1D array with interleaved channels.
        interleaved = np.frombuffer(buffer, dtype=f"int{f.getsampwidth()*8}")
        # Reshape it into a 2D array separating the channels in columns.
        return interleaved # np.reshape(interleaved, (-1, f.getnchannels()))


def record():
    stream = audio.open(
        format=FORMAT,
        channels=CHANNELS,
        rate=RATE,
        input=True,
        frames_per_buffer=CHUNK,
    )

    data = stream.read(CHUNK)
    data = np.fromstring(data, dtype=np.int16)

    stream.stop_stream()
    stream.close()
    audio.terminate()

    return data


def save(data, fname="file.wav"):
    waveFile = wave.open(fname, "wb")
    waveFile.setnchannels(CHANNELS)
    waveFile.setsampwidth(audio.get_sample_size(FORMAT))
    waveFile.setframerate(RATE)
    waveFile.writeframes(b"".join(data.astype(np.int16)))
    waveFile.close()
