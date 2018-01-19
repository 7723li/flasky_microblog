import requests
import json
import base64
import wave
import io
import uuid
from pydub import AudioSegment

class BaiduRest:
    def __init__(self, cu_id, api_key, api_secert):
        self.token_url = "https://openapi.baidu.com/oauth/2.0/token"    # token认证的url
        self.getvoice_url = "http://tsn.baidu.com/text2audio"           # 语音合成的resturl
        self.upvoice_url = 'http://vop.baidu.com/server_api'            # 语音识别的resturl
        self.cu_id = cu_id
        self.getToken(api_key, api_secert)
        return

    def getToken(self, api_key, api_secert):
        data={'grant_type':'client_credentials','client_id':api_key,'client_secret':api_secert}
        r=requests.post(self.token_url,data=data)
        Token=json.loads(r.text)
        self.token_str = Token['access_token']


    def getVoice(self, text, filename):
        data={'tex':text,'lan':'zh','cuid':self.cu_id,'ctp':1,'tok':self.token_str}
        r=requests.post(self.getvoice_url,data=data,stream=True)
        voice_fp = open(filename,'wb')
        voice_fp.write(r.raw.read())
        voice_fp.close()


    def getText(self, filename):
        data = {"format":"wav","rate":16000, "channel":1,"token":self.token_str,"cuid":self.cu_id,"lan":"zh"}
        wav_fp = open(filename,'rb')
        voice_data = wav_fp.read()
        data['len'] = len(voice_data)
        data['speech'] = base64.b64encode(voice_data).decode('utf-8')
        post_data = json.dumps(data)
        r=requests.post(self.upvoice_url,data=bytes(post_data,encoding="utf-8"))
        return r.text

    def ConvertToWav(self,filename,wavfilename):
        #先从本地获取mp3的bytestring作为数据样本
        fp=open(filename,'rb')
        data=fp.read()
        fp.close()
        #主要部分
        aud=io.BytesIO(data)
        sound = AudioSegment.from_file(aud,format='mp3')
        raw_data = sound._data
        #写入到文件，验证结果是否正确。
        l=len(raw_data)
        f=wave.open(wavfilename,'wb')
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(16000)
        f.setnframes(l)
        f.writeframes(raw_data)
        f.close()
        return wavfilename

def main():
    api_key = "V9fQYQSsMNlvTA5bRukcfuvy" 
    api_secert = "a8c045169d9e48eecbc6ae5ef31f8a0b"
    mac=uuid.UUID(int = uuid.getnode()).hex[-12:]
    bdr = BaiduRest(mac, api_key, api_secert)             # 初始化
    bdr.getVoice("今天气温，26，度", "out.mp3")           # 将字符串语音合成并保存为out.mp3
    wav_filename = bdr.ConvertToWav("out.mp3","test.wav") # 将mp3格式转换成wav格式
    print(bdr.getText(wav_filename))                      # 识别test.wav语音内容并显示

# main()
