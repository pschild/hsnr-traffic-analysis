import cv2
import numpy as np
import time
from imutils.video.pivideostream import PiVideoStream

startTime = time.time()
lastFrameTime = startTime
intervalInSec = 2.0
frameCounter = 0

cap = PiVideoStream().start()
time.sleep(2.0)
#videoFps = cap.get(cv2.CAP_PROP_FPS)

base = np.zeros((240,320) + (3,), dtype='uint8')
#base = np.zeros((480,640) + (3,), dtype='uint8')
#base = np.zeros((638,1280) + (3,), dtype='uint8')
#AREA_PTS = np.array([[268,354], [519,436], [403,632], [15,632]])
AREA_PTS = np.array([[0,0], [100,0], [100,100]])
area_mask = cv2.fillPoly(base, [AREA_PTS], (255, 255, 255))[:, :, 0]
all = np.count_nonzero(area_mask)

def logToFile(second, capacity):
	f = file('./carCounter.log','a')
	timestamp = time.strftime("%Y%m%d-%H%M%S")
	output = timestamp + ';' + str(second) + ';' + str(capacity) + "\r\n"
	f.write(output)
	f.close()

def printMouseCoords(event, x, y, flags, param):
	if event == cv2.EVENT_LBUTTONDBLCLK:
		print "Mouse at ({},{})".format(x, y)

cv2.namedWindow('img')
cv2.setMouseCallback('img', printMouseCoords)

while 1:
	frame = cap.read()
	frameCounter += 1

	if (time.time() - lastFrameTime >= intervalInSec):
		frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
		clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
		cl1 = clahe.apply(frame)

		edges = cv2.Canny(frame,50,70)
		edges = ~edges

		blur = cv2.bilateralFilter(cv2.blur(edges,(21,21), 100),9,200,200)

		_, threshold = cv2.threshold(blur,220,255,cv2.THRESH_BINARY)
		t = cv2.bitwise_and(threshold,threshold,mask = area_mask)

		free = np.count_nonzero(t)
		capacity = 1 - float(free) / all

		#print "cap: {0}".format(capacity)
		print "{}".format(time.time())
		#currentSecond = frameCounter / videoFps
		#logToFile(currentSecond, capacity)

		lastFrameTime = time.time()

		#cv2.imshow('img',edges)

	#cv2.fillPoly(frame, [AREA_PTS], (255, 0, 0))

	cv2.imshow('img',frame)
	k = cv2.waitKey(30) & 0xff
	if k == 27:
		break

cv2.destroyAllWindows()
cap.stop()
