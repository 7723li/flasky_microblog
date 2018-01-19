from baidu_speech import BaiduRest
from pyaudio_test import wave_record
import uuid
import time
import os
import json

basedir = os.path.abspath(os.path.dirname(__file__))
record_wav = 'record.wav'
temp_mp3 = basedir + '\\temp.mp3'
synthesis_wav = 'synthesis.wav'

api_key = "V9fQYQSsMNlvTA5bRukcfuvy"
api_secert = "a8c045169d9e48eecbc6ae5ef31f8a0b"
mac = uuid.UUID(int = uuid.getnode()).hex[-12:]

test = wave_record()
bdr = BaiduRest(mac, api_key, api_secert)

def wait():
    for i in range(3,0,-1):
        print( 'prepare to record in {} second'.format(str(i)) )
        time.sleep(1)

def record(): # 录音
    test.record(record_wav)

def distinguish(): # 识别
    return bdr.getText(record_wav)

def synthesis(text): # 合成
    bdr.getVoice(text, temp_mp3)

def play(): #播放
    bdr.ConvertToWav(temp_mp3 , synthesis_wav)
    os.remove(temp_mp3)
    test.play( synthesis_wav )

def main():
    wait()
    record()
    text = json.loads(distinguish())
    print( text )
    try:
        text = text['result'][0]
    except:
        text = '发生了一点错误'
    synthesis(text)
    play()

    
