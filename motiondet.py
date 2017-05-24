#!/usr/bin/python
# import the necessary packages
import argparse
import datetime
import imutils
import time
import cv2
from email.mime.text import MIMEText
import threading
area=0
def signalAlert():
    #Body of the message
    msg = MIMEText("Nothing else matters")
    #Corollary
    msg['Subject']="tera_buddha_gir_gaya"
    msg['From']="leonabrocks@yahoo.com"
    recipients = ["leonabrocks12@gmail.com","aubhik.mazumdar@gmail.com","abhisargarg@live.com"]
    msg['To']= ", ".join(recipients)
    try:
        s = smtplib.SMTP('smtp.gmail.com',587)
        s.starttls()
        #WE NEED TO MAKE A GOOGLE ACC FOR THIS, OR IF SOMEONE WANTS TO VOLUNTEER THEIR PASSWORD o:)
        s.login("aubhik.mazumdar@gmail.com","YouTHinkImStupid??")
        s.send_message(msg)
        s.quit()
        print("Email sent")
        return True
    except:
        print("Error")
        return False


# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-a", "--min-area", type=int, default=800, help="minimum area size")
args = vars(ap.parse_args())
 
# if the video argument is None, then we are reading from webcam
if args.get("video", None) is None:
	camera = cv2.VideoCapture(0)
	time.sleep(0.25)
# otherwise, we are reading from a video file
else:
	camera = cv2.VideoCapture(args["video"])
 
# initialize the first frame in the video stream
avg = None
flag=0
# loop over the frames of the video
while True:
	#recalibrate the level
	yhigh=250
	# grab the current frame and initialize the occupied/unoccupied
	# text
	(grabbed, frame) = camera.read()
	text = "Unoccupied"
 
	# if the frame could not be grabbed, then we have reached the end
	# of the video
	if not grabbed:
		break
 
	# resize the frame, convert it to grayscale, and blur it
	frame = imutils.resize(frame, width=500)
	gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
	gray1 = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
	gray = cv2.GaussianBlur(gray, (21, 21), 0)
	faceCascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
	faces = faceCascade.detectMultiScale(
    gray1,
    scaleFactor=1.1,
    minNeighbors=5,
    minSize=(30, 30),
    flags = cv2.CASCADE_SCALE_IMAGE
    )

    	for (x, y, w, h) in faces:
    		cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 255), 2)
    		area=w*h
    		if y<yhigh:
    			yhigh=y

	if avg is None:
		print "[INFO] starting background model..."
		avg = gray.copy().astype("float")
		continue

	# accumulate the weighted average between the current frame and
	# previous frames, then compute the difference between the current
	# frame and running average
	cv2.accumulateWeighted(gray, avg, 0.5)
	frameDelta = cv2.absdiff(gray, cv2.convertScaleAbs(avg))

	# threshold the delta image, dilate the thresholded image to fill
	# in holes, then find contours on thresholded image
	thresh = cv2.threshold(frameDelta, 5, 255, cv2.THRESH_BINARY)[1]
	thresh = cv2.dilate(thresh, None, iterations=2)
	(_, cnts, _) = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
	
	# loop over the contours
	for c in cnts:
		# if the contour is too small, ignore it
		if cv2.contourArea(c) < 500:
			continue

		# compute the bounding box for the contour, draw it on the frame,
		# and update the text
		
		(x, y, w, h) = cv2.boundingRect(c)
		cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
		#text = "Occupied"

	if flag==0:
	 	yglo=yhigh
	 	flag=1
	 	continue	

	if yglo<yhigh and area<15000 and (yhigh-yglo)>50 and flag==1 and yhigh!=250:
		text="Occupied/Falling"
		print("FALL {} {} {}".format(yhigh,yglo,area))
		yglo=yhigh
    flag=0
        
		# thr = threading.Thread(target=signalAlert, args=(), kwargs={})
		# thr.start()
	if yglo>yhigh:
		flag=0
	

	cv2.putText(frame, "Room Status: {}, yglo: {}, yhigh: {},Area: {}".format(text,yglo,yhigh,area), (10, 20),
		cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
	cv2.putText(frame, datetime.datetime.now().strftime("%A %d %B %Y %I:%M:%S%p"),
		(10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)
	# show the frame and record if the user presses a key
	cv2.imshow("Security Feed", frame)
	cv2.imshow("Thresh", thresh)
	cv2.imshow("Frame Delta", frameDelta)
	key = cv2.waitKey(1) & 0xFF
 
	# if the `q` key is pressed, break from the lop
	if key == ord("q"):
		break
 
# cleanup the camera and close any open windows
camera.release()
cv2.destroyAllWindows()
