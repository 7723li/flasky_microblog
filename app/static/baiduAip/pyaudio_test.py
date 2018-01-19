from pyaudio import PyAudio,paInt16
import wave
import time

class wave_record(object):
	def __init__(self):
		self.framerate = 8000 # 采样频率 8000 or 16000
		self.NUM_SAMPLES = 2000 # 一次性录音采样字节大小
		self.channels = 1 # 声道
		self.sampwidth = 2 # 采样字节 1 or 2
		self.TIME = 2 * 6 * 2 # 控制录音时间 应为 积的1/4

	# 读Wav文件
	def read(self,filename):
		fp = wave.open(filename,'rb')
		nf = fp.getframes()#获取文件的采样点数量
		print('sampwidth:',fp.getsampwidth())
		print('framerate:',fp.getframerate())
		print('channels:',fp.getnchannels())
		f_len=nf*2#文件长度计算，每个采样2个字节
		audio_data=fp.readframes(nf)

	def save(self,filename,data):
		wf = wave.open(filename,'wb')
		wf.setnchannels(self.channels)#声道
		wf.setsampwidth(self.sampwidth)#采样字节 1 or 2
		wf.setframerate(self.framerate)#采样频率 8000 or 16000
		wf.writeframes(b"".join(data))
		wf.close()

	def record(self,filename):
		audio = PyAudio()
		stream = audio.open(
			format = paInt16,channels = 1,
			rate = self.framerate,input = True,
			frames_per_buffer = self.NUM_SAMPLES)
		my_buf = []
		count = 0
		while count < int( self.TIME  ): 
			string_audio_data = stream.read(self.NUM_SAMPLES)#一次性录音采样字节大小
			my_buf.append(string_audio_data)
			count += 1
			print(".")
		self.save(filename,my_buf)
		stream.close()

	def play(self,filename):
		wf = wave.open(filename,'rb')
		p = PyAudio()
		stream = p.open(
			format = p.get_format_from_width(wf.getsampwidth()),
			channels = wf.getnchannels(),
			rate = wf.getframerate(), output = True,)
		start = time.time()
		while time.time()-start <= self.TIME :
			data = wf.readframes(2014)
			if data == "":
				break
			stream.write(data)
		stream.close()
		p.terminate()

def main():
        test = wave_record()
        filename = 'record.wav'
        test.record(filename)
        test.play(filename)

# main()
	
