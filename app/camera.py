#from VideoCapture import Device
from PIL import Image
import cv2
import numpy as np

class VideoCamera(object):
	"""docstring for VideoCamera"""
	def __init__(self):
		super(VideoCamera, self).__init__()
		self.color = (0,0,0)
#		self.classfier=cv2.CascadeClassifier(r"C:\Users\Administrator\Desktop\flasky\haarcascade_frontalface_default.xml")
		self.video = cv2.VideoCapture(0)

	def __del__(self):
		self.video.release()

	def get_frame(self):
		success, image = self.video.read()
#		size=image.shape[:2]
#		frame=np.zeros(size,dtype=np.float16)
#		frame = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
#		cv2.equalizeHist(frame, frame)
#		divisor=8
#		h, w = size
#		minSize=(int(w/divisor), int(h/divisor))
#		faceRects = self.classfier.detectMultiScale(frame, 1.2, 2, cv2.CASCADE_SCALE_IMAGE,minSize)
#		if len(faceRects)>0:
#                    for faceRect in faceRects:
#                            x, y, w, h = faceRect
#                            cv2.rectangle(image, (x, y), (x+w, y+h), self.color)
#		image = Image.fromarray(image)
		ret, jpeg = cv2.imencode('.jpg', image)
		return jpeg.tostring()
