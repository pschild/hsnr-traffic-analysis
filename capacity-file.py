import cv2
import numpy as np
import time

frameCounter = 0
countedSeconds = 0
logInterval = 5 # in seconds

# time when script started
global starttime
starttime = time.strftime("%Y-%m-%d_%H-%M-%S")

# load file
cap = cv2.VideoCapture("../traffic_jam1.mp4")
# get fps of loaded video file
videoFps = cap.get(cv2.CAP_PROP_FPS)

# create a zero for each pixel (according to video size/resolution)
base = np.zeros((480,640) + (3,), dtype='uint8')
# define polygon in which the capacity should be calculated
AREA_PTS = np.array([[100,60], [250,60], [250,150], [100,150]])
# create a mask, based on AREA_PTS, and fill with white pixels
area_mask = cv2.fillPoly(base, [AREA_PTS], (255, 255, 255))[:, :, 0]
# count the number of non-zero values
all = np.count_nonzero(area_mask)

# temporary variables
global min
global avg
global cnt
global sum

# initialization
min = 1.0
avg = 0.0
cnt = 0
sum = 0

# function to update variables
def updateStats(capacity):
	global cnt
	global sum
	global min
	global avg

	cnt += 1
	sum += capacity

	# set new minimum value, if new value is less than old minimum
	if (capacity < min):
		min = capacity

	avg = sum / cnt

# function to reset values
def resetValues():
	global cnt
	global sum
	global avg

	cnt = 0
	sum = 0
	avg = 0.0

# function to write data to file
def logToFile(countedSeconds, min, avg):
	global starttime

	f = file('./cap-file-'+starttime+'.log','a')
	timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
	output = timestamp + ';' + str(countedSeconds) + ';' + str(min) + ';1;' + str(avg) + "\r\n"
	f.write(output)
	f.close()

# function to log mouse coords to console
def printMouseCoords(event, x, y, flags, param):
	if event == cv2.EVENT_LBUTTONDBLCLK:
		print "Mouse at ({},{})".format(x, y)

# prepare windows for opencv and mouse listener
cv2.namedWindow('original')
cv2.setMouseCallback('original', printMouseCoords)

# infinite loop
while 1:
	# 1) read the next frame
	ret, frame = cap.read()
	frameCounter += 1

	# log depending on interval
	if (frameCounter % (videoFps * logInterval) == 0):
		countedSeconds += logInterval
		logToFile(countedSeconds, min, avg)
		print "second={}, min={}, avg={}".format(countedSeconds, min, avg)
		resetValues()

	# 2) convert current frame to gray
	frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

	# 3) do edge detection on grayscaled frame
	edges = cv2.Canny(frame,50,70)
	edges = ~edges

	# 4) blur detected edges
	blur = cv2.bilateralFilter(cv2.blur(edges,(21,21), 100),9,200,200)

	# 5) apply threshold to frame: depending on pixel value, an array of 1s and 0s is created
	_, threshold = cv2.threshold(blur,230,255,cv2.THRESH_BINARY)
	# only apply to masked area
	t = cv2.bitwise_and(threshold,threshold,mask = area_mask)

	# count white pixels within defined polygon/mask
	free = np.count_nonzero(t)
	# calculate capacity in %
	capacity = 1 - float(free) / all

	# update variables
	updateStats(capacity)

	# remove comment to visualize counting area
	#cv2.fillPoly(frame, [AREA_PTS], (255, 0, 0))

	# show original frame
	cv2.imshow('original',frame)

	# wait for "ESC" being pressed to leave infinite loop
	k = cv2.waitKey(30) & 0xff
	if k == 27:
		break

cap.release()
cv2.destroyAllWindows()