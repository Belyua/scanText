import cv2
import imutils

from PIL import Image
from io import BytesIO
from eyes import four_point_transform
from skimage.filters import threshold_local


def main(msg):
	binary_stream = BytesIO()
	# Load the photo using cv2.imread
	image = cv2.imread(msg)
	ratio = image.shape[0] / 500.0
	orig = image.copy()
	image = imutils.resize(image, height=500)
	# convert the image to grayscale, blur it, and find edges in the image
	gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
	gray = cv2.GaussianBlur(gray, (5, 5), 0)
	edged = cv2.Canny(gray, 50, 100)
	#print("STEP 1: Edge Detection")
	cnts = cv2.findContours(edged.copy(), mode=cv2.RETR_EXTERNAL, method=cv2.CHAIN_APPROX_NONE)
	cnts = imutils.grab_contours(cnts)
	cnts = sorted(cnts, key=cv2.contourArea, reverse=True)[:5]
	# loop over the contours
	for c in cnts:
		# approximate the contour
		peri = cv2.arcLength(c, True)
		approx = cv2.approxPolyDP(c, 0.02 * peri, True)
		# if our approximated contour has four points, then we
		# can assume that we have found our screen
		if len(approx) == 4:
			screenCnt = approx
			break
	#print("STEP 2: Find contours of paper")
	# apply the four point transform to obtain a top-down
	warped = four_point_transform(orig, screenCnt.reshape(4, 2) * ratio)
	# convert the warped image to grayscale, then threshold it
	# to give it that 'black and white' paper effect
	warped = cv2.cvtColor(warped, cv2.COLOR_BGR2GRAY)
	T = threshold_local(warped, 11, offset=10, method="gaussian")
	warped = (warped > T).astype("uint8") * 255
	#print("STEP 3: Apply perspective transform")
	img = Image.fromarray(warped)
	img.save(binary_stream, format='jpeg')
	binary_stream.seek(0)
	return binary_stream


if __name__ == '__main__':
	main()