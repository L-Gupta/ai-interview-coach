#Code 1
from google.cloud import speech_v1 as speech
import os
from pydub import AudioSegment
import wave

#kuch to kra samaj ni aaya
with wave.open("audio_sample.wav","rb") as wav_file:
    sample_rate = wav_file.getframerate()
    print("Sample rate" + sample_rate)

#iska bhi purpose samaj ni aaya
client = speech.SpeechClient.from_service_account_file('gcp_key.json')

#apparently all audio needs to be in mono form and not stereo
def convert_to_mono(input_file, output_file):
    audio = AudioSegment.from_file(input_file)
    audio = audio.set_channels(1)
    audio.export(output_file, format = "wav")
    print("Converted to mono")

#finally transcribing audio from speech to text
def transcribe_audio(input_file):
    with open (input_file, 'rb') as audio_file:
        content = audio_file.read()
        audio = speech.RecognitionAudio(content=content)
        config = speech.RecognitionConfig(
                encoding = speech.RecognitionConfig.AudioEncoding.LINEAR16,
                sample_rate_hertz = sample_rate,
                language_code = "en-US"
            )
        response = client.recognize(config=config,audio=audio)

        #why have we used indexing
        for result in response.results:
            print("Transcript" + result.alternatives[0].transcript) 
            print("Confidence" + result.alternatives[0].confidence)
        
        return response

convert_to_mono("audio_sample.wav", "audio_sample_mono_wav")
transcribe_audio("audio_sample_mono.wav")


        
