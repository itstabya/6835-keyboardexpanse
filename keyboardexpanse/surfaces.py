from dataclasses import dataclass
from typing import Optional
import numpy as np
import cv2

from keyboardexpanse.utils import condenseToNPoints, contourOffset, fourCornersSort, weighted_mean

KEYBOARD_SCALE = np.array([[0, 0], [0, 500], [1000, 500], [1000, 0]], np.float32)
DEFAULT_KEYBOARD_SURFACE = np.array([[180, 60], [35, 450], [830, 415], [660, 50]])


def transform_points(points, s_points, t_points):
        # getPerspectiveTransform() needs float32
    if s_points.dtype != np.float32:
        s_points = s_points.astype(np.float32)
    if t_points.dtype != np.float32:
        t_points = t_points.astype(np.float32)

    def point_transform(point):
        point = np.append(point.astype(np.float32), 1)
        M = cv2.getPerspectiveTransform(s_points, t_points)

        t = np.dot(M, point)
        return (t[:2] / t[2]).astype(np.int32)

    return (
        np.array([point_transform(p) for p in points], dtype=np.int32)
        if len(points.shape) > 1
        else point_transform(points)
    )

@dataclass
class DetectSurfaces:
    surface_camspace: Optional[np.array] = None
    surface_confirmations: int = 0
    
    background_colours = [
        # MacGregor (wood) desks :P
        ([0, 92, 39], [178, 216, 255]),
        # Hands
        # ([0, 30, 78], [179, 112, 225]),
        # Wire
        ([0, 18, 50], [178, 60, 79]),
        # Light Wood
        ([2, 16, 174], [19, 158, 201])
    ]

    surfacespace_dimensions: np.array = KEYBOARD_SCALE

    def isolate_surface(self, img):
        s_points = self.surface_camspace
        t_points = self.surfacespace_dimensions

        # getPerspectiveTransform() needs float32
        if s_points.dtype != np.float32:
            s_points = s_points.astype(np.float32)

        M = cv2.getPerspectiveTransform(s_points, t_points)
        return cv2.warpPerspective(img, M, (1000, 500))

    def to_surface_space(self, points):
         return transform_points(points, self.surface_camspace, self.surfacespace_dimensions)

    def to_cam_space(self, points):
        return transform_points(points, self.surfacespace_dimensions, self.surface_camspace)

    def detect(self, img):
         # If the keyboard is stable, don't bother performing
        # detection
        if self.surface_confirmations > 50:
            return img

        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

        # Apply some helpful colour masks
        accumMask = np.zeros(hsv.shape[:2], dtype="uint8")


        # loop over the boundaries
        for (lower, upper) in self.background_colours:
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
        bin_v = cv2.adaptiveThreshold(
            v, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 115, 4
        )

        # Median filter to clear small details
        bin_v = cv2.medianBlur(bin_v, 11)

        # Add a black border to allow laptop to touch edge of screen
        BORDER_SIZE = 20
        bin_v = cv2.copyMakeBorder(
            bin_v,
            BORDER_SIZE,
            BORDER_SIZE,
            BORDER_SIZE,
            BORDER_SIZE,
            cv2.BORDER_CONSTANT,
            value=0,
        )

        # # morphological closing
        # kernel = np.ones((3, 3), np.uint8)
        # v = cv2.morphologyEx(v, cv2.MORPH_CLOSE, kernel, iterations=10)

        edges = cv2.Canny(bin_v, 200, 250)

        # Contours
        contours, hierarchy = cv2.findContours(
            edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE
        )

        height, width = edges.shape
        MIN_CONTOUR_AREA = width * height * 0.5
        MAX_CONTOUR_AREA = (width - BORDER_SIZE) * (height - BORDER_SIZE)

        # Keyboard should fill at least half the image
        maxAreaFound = MIN_CONTOUR_AREA

        if self.surface_camspace is None:
            self.surface_camspace = DEFAULT_KEYBOARD_SURFACE

        simplified = [self.surface_camspace]
        for cnt in contours:
            perimeter = cv2.arcLength(cnt, True)
            ALLOWED_ERROR = 0.03
            approx = cv2.convexHull(cv2.approxPolyDP(cnt, perimeter * ALLOWED_ERROR, True))

            # Check we have a 4 point approximation
            # Total area > 1000
            # Convex contor
            area = cv2.contourArea(approx)
            isAlmostQuad = 4 <= len(approx) < 6
            isLarge = maxAreaFound < area < MAX_CONTOUR_AREA
            
            # isConvex = cv2.isContourConvex(quadApprox)
            if isAlmostQuad and isLarge:
                maxAreaFound = area
                normApprox = contourOffset(approx, (-BORDER_SIZE, -BORDER_SIZE)).squeeze()
                # normApprox = condenseToNPoints(normApprox, N=4)
            
                newContour = fourCornersSort(normApprox)
                print(f"Adjusting Surface {self.surface_confirmations}", newContour)
                self.surface_camspace = weighted_mean(self.surface_camspace, newContour, self.surface_confirmations, default=DEFAULT_KEYBOARD_SURFACE)
                self.surface_confirmations += 1

            if isLarge:
                normApprox = contourOffset(approx, (-BORDER_SIZE, -BORDER_SIZE)).squeeze()
                quadApprox = condenseToNPoints(normApprox, N = 4)
                
                simplified.append(normApprox)
                simplified.append(quadApprox)

        # DEBUG SURFACES WITH:
        # img = edges
        # img = v
        cv2.drawContours(img, simplified, -1, (0, 255, 0), 3)
        for s in simplified:
            for k in s:
                cv2.drawMarker(img, k, (255,255,0))
        return img