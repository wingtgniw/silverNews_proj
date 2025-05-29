from openai import OpenAI
import openai
import os
from playsound import playsound

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

def read_text(file_name, news_type):
    playsound(os.path.join(*[audio_path, news_type, file_name]))