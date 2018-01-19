import RPi.GPIO as gpio
import time,json

def DHT11():
	pass

gpio.setmode(gpio.BOARD)
gpio.setwarnings(False)
time.sleep(1)
data=[]

gpio.setup(12,gpio.OUT)
gpio.setup(16,gpio.OUT)
	
gpio.output(12,gpio.LOW)
time.sleep(0.02)
gpio.output(12,gpio.HIGH)
gpio.output(16,gpio.LOW)

gpio.setup(12,gpio.IN)
while gpio.input(12)==1:
	continue

while gpio.input(12)==0:
	continue

while gpio.input(12)==1:
	continue

#get data
j=0
while j<40:
	k=0
	while gpio.input(12)==0:
		continue
		
	while gpio.input(12)==1:
		k += 1
		if k>100:
			break
#		print(k)
	if k<=10:
		data.append(0)
	else:
		data.append(1)
	j += 1

humidity_bit=data[0:8]
humidity_point_bit=data[8:16]
tempture_bit=data[16:24]
tempture_point_bit=data[24:32]
check_bit=data[32:40]

humidity = 0
humidity_point = 0
tempture = 0
tempture_point = 0
check = 0

for i in range(8):
	humidity += humidity_bit[i]*2**(7-i)
	humidity_point += humidity_point_bit[i]*2**(7-i)
	tempture += tempture_bit[i]*2**(7-i)
	tempture_point += tempture_point_bit[i]*2**(7-i)
	check += check_bit[i]*2**(7-i)

tmp=humidity+humidity_point+tempture+tempture_point
res=json.dumps({'humidity':humidity,'tempture':tempture})
print(res)
gpio.output(16,gpio.HIGH)

#if __name__ == '__main__':
	#DHT11()

