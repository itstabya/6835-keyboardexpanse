import cv2
import numpy as np
import keyboardexpanse.hands.detector as detector
import time

# import autopy
from screeninfo import get_monitors

# import pyautogui

from keyboardexpanse.hands.detector import Handness
from keyboardexpanse.hands.gesture import HandAnalysis
from keyboardexpanse.hands.landmarks import HandLandmark
from keyboardexpanse.relay import Relay

##########################
wCam, hCam = 900, 500
FRAME_RATE_DELAY = 0
IS_MIRRORED_DOWN = True
#########################


def simulate_on_move(x, y):
    # pyautogui.moveTo(x, y)
    # autopy.mouse.move(x, y)
    ...


def resize(img, height=800):
    rat = height / img.shape[0]
    return cv2.resize(img, (int(rat * img.shape[1]), height))


def fourCornersSort(pts):
    """Sort corners: top-left, bot-left, bot-right, top-right"""
    # Difference and sum of x and y value
    # Inspired by http://www.pyimagesearch.com
    diff = np.diff(pts, axis=1)
    summ = pts.sum(axis=1)

    # Top-left point has smallest sum...
    # np.argmin() returns INDEX of min
    return np.array(
        [
            pts[np.argmin(summ)],
            pts[np.argmax(diff)],
            pts[np.argmax(summ)],
            pts[np.argmin(diff)],
        ]
    )


def weighted_mean(og_bounds, new_bounds, weight):
    pts = np.array(DEFAULT_KEYBOARD_CONTOUR)
    for i in range(4):
        pts[i] = (og_bounds[i] * weight + new_bounds[i]) / (weight + 1)
    return pts


DEFAULT_KEYBOARD_CONTOUR = np.array([[180, 60], [35, 450], [830, 415], [660, 50]])
keyboardContour = None
keyboardWeight = 0


def detect_laptop_surface(img):
    global keyboardContour
    global keyboardWeight

    # If the keyboard is stable, don't bother performing
    # detection
    if keyboardWeight > 10:
        return img

    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # Apply some helpful colour masks
    accumMask = np.zeros(hsv.shape[:2], dtype="uint8")

    # define the list of color boundaries
    boundaries = [
        # MacGregor desks :P
        ([0, 92, 39], [178, 216, 255]),
    ]

    # loop over the boundaries
    for (lower, upper) in boundaries:
        # create NumPy arrays from the boundaries
        lower = np.array(lower, dtype="uint8")
        upper = np.array(upper, dtype="uint8")

        # find the colors within the specified boundaries
        mask = cv2.inRange(hsv, lower, upper)

        # merge the mask into the accumulated masks
        accumMask = cv2.bitwise_or(accumMask, mask)

    accumMask = cv2.bitwise_not(accumMask)

    hsv = cv2.bitwise_and(hsv, hsv, mask=accumMask)

    # Apply some thresholds
    h, s, v = cv2.split(hsv)

    # Binary image from adaptive thresholds
    v = cv2.adaptiveThreshold(
        v, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 115, 4
    )

    # Median filter to clear small details
    v = cv2.medianBlur(v, 11)

    # Add a black border to allow laptop to touch edge of screen
    v = cv2.copyMakeBorder(v, 5, 5, 5, 5, cv2.BORDER_CONSTANT, value=[0, 0, 0])

    edges = cv2.Canny(v, 200, 250)

    # Contours
    contours, hierarchy = cv2.findContours(
        edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE
    )

    height, width = edges.shape
    MIN_CONTOUR_AREA = width * height * 0.5
    MAX_CONTOUR_AREA = (width - 10) * (height - 10)

    # Keyboard should fill at least half the image
    maxAreaFound = MIN_CONTOUR_AREA

    if keyboardContour is None:
        keyboardContour = DEFAULT_KEYBOARD_CONTOUR

    for cnt in contours:
        perimeter = cv2.arcLength(cnt, True)
        ALLOWED_ERROR = 0.03
        approx = cv2.approxPolyDP(cnt, perimeter * ALLOWED_ERROR, True)

        # Check we have a 4 point approximation
        # Total area > 1000
        # Convex contor
        # maxCosine < .3 for all four points

        area = cv2.contourArea(approx)
        isQuad = len(approx) == 4
        isLarge = maxAreaFound < area < MAX_CONTOUR_AREA
        isConvex = cv2.isContourConvex(approx)
        if isLarge and isQuad and isConvex:
            maxAreaFound = area
            newContour = fourCornersSort(approx[:, 0])
            print(f"Adjusting Keyboard {keyboardWeight}", newContour)
            keyboardContour = weighted_mean(keyboardContour, newContour, keyboardWeight)
            keyboardWeight += 1

    # img = v
    cv2.drawContours(img, [keyboardContour], -1, (0, 255, 0), 3)
    return img


def perspective_transform(img, s_points):
    # Transform start points to target points
    # Euclidean distance - calculate maximum height and width
    height = max(
        np.linalg.norm(s_points[0] - s_points[1]),
        np.linalg.norm(s_points[2] - s_points[3]),
    )
    width = max(
        np.linalg.norm(s_points[1] - s_points[2]),
        np.linalg.norm(s_points[3] - s_points[0]),
    )

    # Create target points
    t_points = np.array([[0, 0], [0, height], [width, height], [width, 0]], np.float32)

    # getPerspectiveTransform() needs float32
    if s_points.dtype != np.float32:
        s_points = s_points.astype(np.float32)

    M = cv2.getPerspectiveTransform(s_points, t_points)
    return cv2.warpPerspective(img, M, (int(width), int(height)))


def main():
    """Launch Keyboard Expanse."""

    r = Relay()
    # r.start()

    pTime = 0

    cap = cv2.VideoCapture(0)
    cap.set(3, wCam)
    cap.set(4, hCam)
    handDetector = detector.HandDetector(maxHands=2)
    handAnalyser = HandAnalysis(
        detector=handDetector,
        wCam=wCam,
        hCam=hCam,
    )
    handAnalyser.detect_monitors()
    handAnalyser.register_hooks(on_move=simulate_on_move)

    try:
        while True:
            # 1. Find hand Landmarks
            _, img = cap.read()
            # mirror image for convenience
            img = cv2.flip(img, 2)

            # Flip if mirrored down
            if IS_MIRRORED_DOWN:
                img = cv2.flip(img, 0)

            img = detect_laptop_surface(img)

            # img = handAnalyser.step(img)

            # 11. Frame Rate
            cTime = time.time()
            fps = 1 / (cTime - pTime)

            if (cTime - pTime) < FRAME_RATE_DELAY:
                time.sleep(FRAME_RATE_DELAY - (cTime - pTime))

            pTime = cTime
            cv2.putText(
                img, str(int(fps)), (20, 50), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 0), 3
            )

            keyboard_view = cv2.flip(perspective_transform(img, keyboardContour), 0)

            # 12. Display
            cv2.imshow("Annotated WebCam", img)
            cv2.imshow("Keyboard", keyboard_view)
            cv2.waitKey(1)

    except KeyboardInterrupt:
        pass

    # After the loop release the cap object
    cap.release()
    # Destroy all the windows
    cv2.destroyAllWindows()

    r.clean()


if __name__ == "__main__":
    main()
