import numpy as np
import sounddevice as sd
from kokoro import KPipeline

def play_audio(audio, sample_rate=24000):
    # Normalize audio to 16-bit PCM if it's not already
    audio = np.array(audio)
    if np.max(np.abs(audio)) > 0:
        audio = audio / np.max(np.abs(audio))
    audio_int16 = (audio * 32767).astype(np.int16)
    
    # Play audio (non-blocking call can be set up with a callback if needed)
    sd.play(audio_int16, samplerate=sample_rate)
    sd.wait()  # Wait until playback is done

def main():
    pipeline = KPipeline(lang_code='a')
    text = "Hello, I am your voice assistant."
    
    # Generate the audio segment
    for gs, ps, audio in pipeline(text, voice='af_heart', speed=1, split_pattern=r'\n+'):
        play_audio(audio)
        break  # Play the first generated segment

if __name__ == "__main__":
    main()