import numpy as np
import cv2
from shapely.geometry import Polygon
import time

startTime = time.time()
lastFrameTime = startTime
intervalInSec = 2.0
frameCounter = 0

#AREA1 = [[73,62], [153,62], [637,330], [637,418], [528,419]]
#AREA2 = [[2,64], [50,63], [474,420], [226,419], [3, 93]]
AREA1 = [[268,354], [519,436], [403,632], [15,632]]

car_cascade = cv2.CascadeClassifier('../cars.xml')

cap = cv2.VideoCapture("../traffic_sim.mp4")
videoFps = cap.get(cv2.CAP_PROP_FPS)

def logToFile(second, areaId, carCount):
	f = file('./carCounter.log','a')
	timestamp = time.strftime("%Y%m%d-%H%M%S")
	output = timestamp + ';' + str(second) + ';' + str(areaId) + ';' + str(carCount) + "\r\n"
	f.write(output)
	f.close()

def printMouseCoords(event, x, y, flags, param):
	if event == cv2.EVENT_LBUTTONDBLCLK:
		print "Mouse at ({},{})".format(x, y)

cv2.namedWindow('img')
cv2.setMouseCallback('img', printMouseCoords)

while 1:
	ret, img = cap.read()
	frameCounter += 1

	gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

	# Detect cars every n seconds
	if (time.time() - lastFrameTime >= intervalInSec):
		cars = car_cascade.detectMultiScale(gray, 1.1, 2)

		# Draw border
		a1Cars = 0
		#a2Cars = 0
		for (x, y, w, h) in cars:
			cv2.rectangle(img, (x,y), (x+w,y+h), (0,0,255), 2)

			p1 = Polygon([(x,y),(x+w,y),(x+w,y+h),(x,y+h)])
			if p1.intersects(Polygon(AREA1)):
				a1Cars = a1Cars + 1
			#elif p1.intersects(Polygon(AREA2)):
				#a2Cars = a2Cars + 1

		print "nach oben: {} {}".format(time.time() - startTime, a1Cars)
		#print "nach unten: {} {}".format(time.time() - startTime, a2Cars)
		#print "{} {}".format(frameCounter, frameCounter / videoFps)
		currentSecond = frameCounter / videoFps
		#logToFile(currentSecond, 1, a1Cars)
		#logToFile(currentSecond, 2, a2Cars)

		lastFrameTime = time.time()

	area1 = np.array(AREA1)
	#area2 = np.array(AREA2)
	cv2.polylines(img, [area1], 1, (0,255,0))
	#cv2.polylines(img, [area2], 1, (255,0,0))

	cv2.imshow('img',img)
	k = cv2.waitKey(30) & 0xff
	if k == 27:
		break

cap.release()
cv2.destroyAllWindows()