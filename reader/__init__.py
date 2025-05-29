from openai import OpenAI
import multiprocessing, openai, os
from playsound import playsound
import streamlit as st

openai.api_key = os.getenv("OPENAI_API_KEY")

client = OpenAI()

audio_path = './audio'
if not os.path.exists(audio_path):
    os.makedirs(os.path.join(audio_path, 'newsletter'))
    os.makedirs(os.path.join(audio_path, 'article'))

def save_audio(text, file_name, news_type):

    save_path = os.path.join(*[audio_path, news_type, file_name])
    if os.path.exists(save_path):
        return
    
    response = client.audio.speech.create( model='tts-1',
                            input=text,
                            voice='nova')

    with open(save_path, 'wb') as fp:
        fp.write(response.content)

class ReadManager:
    def __init__(self):
        self.played_process = None
        self.played_file_name = None
        self.clicked_play_button_key = None

    def read_text(self, file_name, news_type):
        if self.played_process is not None:
            
            if self.played_file_name == file_name:
                print(f"ReadManager ---- {file_name} is already playing")
                self.stop_read_text()
                return
            else:
                self.stop_read_text()

        p = multiprocessing.Process(target=playsound, args=(os.path.join(*[audio_path, news_type, file_name]),))
        p.start()

        self.played_process = p
        self.played_file_name = file_name

    def stop_read_text(self):
        if self.played_process is not None:
            try:
                self.played_process.terminate()
            except Exception as e:
                print(f"Error stopping audio: {str(e)}")
            finally:
                self.played_process = None
                self.played_file_name = None