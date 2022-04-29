import time
import cv2
import numpy as np
from threading import Timer

def resize(img, height=800):
    rat = height / img.shape[0]
    return cv2.resize(img, (int(rat * img.shape[1]), height))


def one_per(s):
    """Decorator ensures function that can only be called once every `s` seconds.
    """
    def decorate(f):
        t = None

        def wrapped(*args, **kwargs):
            nonlocal t
            t_ = time.time()
            if t is None or t_ - t >= s:
                result = f(*args, **kwargs)
                t = time.time()
                return result
        return wrapped
    return decorate

def debounce(wait):
    """ Decorator that will postpone a functions
        execution until after wait seconds
        have elapsed since the last time it was invoked. """
    def decorator(fn):
        def debounced(*args, **kwargs):
            def call_it():
                fn(*args, **kwargs)
            try:
                debounced.t.cancel()
            except(AttributeError):
                pass
            debounced.t = Timer(wait, call_it)
            debounced.t.start()
        return debounced
    return decorator

def condenseToNPoints(pts, N=4):
    # Find the N closest pairs
    # Merge to average values

    # TODO: Divide+Conquer approach would be quicker
    while len(pts) > N:
        k, l = -1, -1
        min_dist = np.inf
        for i, p in enumerate(pts):
            for j, q in enumerate(pts):
                if i == j:
                    continue

                dist = np.linalg.norm(p - q)
                if dist < min_dist:
                    k, l = i, j
                    min_dist = dist

        merged_point = np.mean([pts[k], pts[l]], axis=0)
        pts = np.delete(pts, [l], axis=0)
        pts[k] = merged_point

    return pts.astype(np.int32)


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


def contourOffset(cnt, offset):
    """Offset contour, by border"""
    # Matrix addition
    cnt += offset

    # if value < 0 => replace it by 0
    cnt[cnt < 0] = 0
    return cnt


def weighted_mean(og_bounds, new_bounds, weight, default=[]):
    pts = np.array(default)
    for i in range(4):
        pts[i] = (og_bounds[i] * weight + new_bounds[i]) / (weight + 1)
    return pts


def apply_overlay(img, points, alpha=0.5, color=(0, 255, 0)):
    mask = np.zeros(img.shape, np.uint8)
    mask = cv2.fillPoly(mask, pts=[points], color=color)
    img = cv2.addWeighted(img, 1, mask, 1 - alpha, 0)
    return img
