import cv2
import numpy as np
import time

frameCounter = 0
countedSeconds = 0
logInterval = 5 #seconds

cap = cv2.VideoCapture("../traffic_sim.mp4")
videoFps = cap.get(cv2.CAP_PROP_FPS)

#base = np.zeros((480,640) + (3,), dtype='uint8')
base = np.zeros((638,1280) + (3,), dtype='uint8')
AREA_PTS = np.array([[268,354], [519,436], [403,632], [15,632]])
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

def resetStats():
	global cnt
	global sum
	global min
	global max
	global avg

	cnt = 0
	sum = 0
	min = 1.0
	max = 0.0
	avg = 0.0

def logToFile(countedSeconds, min, max, avg):
	f = file('./carCounter.log','a')
	timestamp = time.strftime("%Y%m%d-%H%M%S")
	output = timestamp + ';' + str(countedSeconds) + ';' + str(min) + ';' + str(max) + ';' + str(avg) + "\r\n"
	f.write(output)
	f.close()

def printMouseCoords(event, x, y, flags, param):
	if event == cv2.EVENT_LBUTTONDBLCLK:
		print "Mouse at ({},{})".format(x, y)

cv2.namedWindow('img')
cv2.setMouseCallback('img', printMouseCoords)

while 1:
	ret, frame = cap.read()
	frameCounter += 1
	# log every second
	if (frameCounter % (videoFps * logInterval) == 0):
		countedSeconds += logInterval
		logToFile(countedSeconds, min, max, avg)
		print "logged"
		resetStats()

	frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
	clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
	cl1 = clahe.apply(frame)

	edges = cv2.Canny(frame,50,70)
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

	cv2.imshow('img',frame)
	k = cv2.waitKey(30) & 0xff
	if k == 27:
		break

cap.release()
cv2.destroyAllWindows()
