import pyaudio

def list_audio_devices():
    audio = pyaudio.PyAudio()
    
    print("\nVerfügbare Audio-Eingabegeräte:")
    print("-" * 50)
    
    try:
        info = audio.get_host_api_info_by_index(0)
        num_devices = info.get('deviceCount')
        
        for i in range(num_devices):
            try:
                device_info = audio.get_device_info_by_index(i)
                if device_info.get('maxInputChannels') > 0:
                    print(f"Index {i}: {device_info.get('name')}")
                    print(f"   Kanäle: {device_info.get('maxInputChannels')}")
                    print(f"   Sample Rate: {device_info.get('defaultSampleRate')}")
                    print("-" * 50)
            except:
                continue
                
    finally:
        audio.terminate()

if __name__ == "__main__":
    list_audio_devices()
