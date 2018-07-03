import cv2
import numpy as np
import time
from RepeatedTimer import RepeatedTimer
from imutils.video.pivideostream import PiVideoStream

frameCounter = 0
countedSeconds = 0
logInterval = 5 #seconds

global starttime
starttime = time.strftime("%Y-%m-%d_%H-%M-%S")

cap = PiVideoStream(resolution=(640,480)).start()
time.sleep(2.0)

base = np.zeros((480,640) + (3,), dtype='uint8')
AREA_PTS = np.array([[252,213], [238,238], [626,365], [632,289]])

area_mask = cv2.fillPoly(base, [AREA_PTS], (255, 255, 255))[:, :, 0]
all = np.count_nonzero(area_mask)

# temporary variables
global min
global max
global avg
global cnt
global sum

min = 1.0
max = 0.0
avg = 0.0
cnt = 0
sum = 0

def updateStats(capacity):
	global cnt
	global sum
	global min
	global max
	global avg

	cnt += 1
	sum += capacity

	if (capacity < min):
		min = capacity

	if (capacity > max):
		max = capacity

	avg = sum / cnt

def resetAverage():
	global cnt
	global sum
	global avg

	cnt = 0
	sum = 0
	avg = 0.0

def logToFile(min, max, avg):
	global starttime

	f = file('./cap-live-'+starttime+'.log','a')
	timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
	output = timestamp + ';' + str(min) + ';' + str(max) + ';' + str(avg) + "\r\n"
	f.write(output)
	f.close()

def printMouseCoords(event, x, y, flags, param):
	if event == cv2.EVENT_LBUTTONDBLCLK:
		print "Mouse at ({},{})".format(x, y)

cv2.namedWindow('img1')
cv2.setMouseCallback('img1', printMouseCoords)

def collect():
	global min
	global max
	global avg

	print "logged@{}, min={}, max={}, avg={}".format(time.time(), min, max, avg)
	logToFile(min, max, avg)
	resetAverage()

rt = RepeatedTimer(logInterval, collect)

while 1:
	frame = cap.read()

	gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
	clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
	cl1 = clahe.apply(gray)

	edges = cv2.Canny(gray,50,70)
	edges = ~edges

	blur = cv2.bilateralFilter(cv2.blur(edges,(21,21), 100),9,200,200)

	_, threshold = cv2.threshold(blur,230,255,cv2.THRESH_BINARY)
	t = cv2.bitwise_and(threshold,threshold,mask = area_mask)

	free = np.count_nonzero(t)
	capacity = 1 - float(free) / all

	#print "cap: {0}".format(capacity)
	updateStats(capacity)
	#print "min={},max={},avg={},sum={},cnt={}".format(min,max,avg,sum,cnt)

	#cv2.fillPoly(frame, [AREA_PTS], (255, 0, 0))

	cv2.imshow('img',t)
	cv2.imshow('img1',frame)
	k = cv2.waitKey(30) & 0xff
	if k == 27:
		break

cv2.destroyAllWindows()
cap.stop()
rt.stop()
