import cv2
import numpy as np
import time
import RepeatedTimer

cap = cv2.VideoCapture("../traffic_sim.mp4")
videoFps = cap.get(cv2.CAP_PROP_FPS)

while 1:
	ret, frame = cap.read()

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

	print "cap: {0}".format(capacity)

	cv2.imshow('img',frame)
	k = cv2.waitKey(30) & 0xff
	if k == 27:
		break

cap.release()
cv2.destroyAllWindows()
