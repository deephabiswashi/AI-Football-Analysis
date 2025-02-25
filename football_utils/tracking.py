import cv2
import numpy as np

def initialize_tracker(frame, bbox):
    """
    Initialize a tracker (e.g., KCF) for a given bounding box.
    """
    tracker = cv2.TrackerKCF_create()
    tracker.init(frame, bbox)
    return tracker

def track_objects(frame, tracker):
    """
    Update tracker for the new frame.
    """
    success, bbox = tracker.update(frame)
    return success, bbox

def calculate_optical_flow(prev_frame, curr_frame):
    """
    Calculate the optical flow between two frames.
    Returns the flow field.
    """
    prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
    curr_gray = cv2.cvtColor(curr_frame, cv2.COLOR_BGR2GRAY)
    flow = cv2.calcOpticalFlowFarneback(prev_gray, curr_gray, None,
                                        0.5, 3, 15, 3, 5, 1.2, 0)
    return flow

def apply_perspective_transform(frame, src_points, dst_points):
    """
    Apply perspective transformation to get a top-down view.
    src_points: 4 points on the input frame.
    dst_points: 4 points on the output plane.
    """
    matrix = cv2.getPerspectiveTransform(src_points, dst_points)
    transformed = cv2.warpPerspective(frame, matrix, (frame.shape[1], frame.shape[0]))
    return transformed
