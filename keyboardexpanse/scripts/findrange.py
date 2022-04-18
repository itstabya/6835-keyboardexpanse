import cv2
import numpy as np

image_hsv = None  # global ;(
pixel = (20, 60, 80)  # some stupid default

min = np.array([256, 256, 256])
max = np.array([-1, -1, -1])

# mouse callback function
def pick_color(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        pixel = image_hsv[y, x]

        # you might want to adjust the ranges(+-10, etc):

        RANGE = 1
        V_RANGE = 2

        upper = np.array([pixel[0] + RANGE, pixel[1] + RANGE, pixel[2] + V_RANGE])
        lower = np.array([pixel[0] - RANGE, pixel[1] - RANGE, pixel[2] - V_RANGE])
        print(pixel, lower, upper)
        print(pixel, min, max)

        for i in range(3):
            if lower[i] < min[i]:
                min[i] = lower[i]
            if upper[i] > max[i]:
                max[i] = upper[i]

        image_mask = cv2.inRange(image_hsv, min, max)
        cv2.imshow("mask", image_mask)


def main():
    import sys

    global image_hsv, pixel  # so we can use it in mouse callback

    cap = cv2.VideoCapture(0)
    wCam, hCam = 900, 500
    cap.set(3, wCam)
    cap.set(4, hCam)
    _, img = cap.read()
    img = cv2.flip(img, 2)
    img = cv2.flip(img, 0)

    cv2.imshow("bgr", img)

    ## NEW ##
    cv2.namedWindow("hsv")
    cv2.setMouseCallback("hsv", pick_color)

    # now click into the hsv img , and look at values:
    image_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    cv2.imshow("hsv", image_hsv)

    cv2.waitKey(0)
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
