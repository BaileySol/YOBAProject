import numpy as np
import cv2
import mediapipe as mp

mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils

def is_full_body_visible(landmarks, visibility_threshold=0.5):
    """
    Check if the full body is visible based on a subset of key landmarks.
    """
    required_points = [
        mp_pose.PoseLandmark.NOSE,
        mp_pose.PoseLandmark.LEFT_SHOULDER,
        mp_pose.PoseLandmark.RIGHT_SHOULDER,
        mp_pose.PoseLandmark.LEFT_HIP,
        mp_pose.PoseLandmark.RIGHT_HIP,
        mp_pose.PoseLandmark.LEFT_ANKLE,
        mp_pose.PoseLandmark.RIGHT_ANKLE,
    ]
    return all(landmarks.landmark[i].visibility >= visibility_threshold for i in required_points)

def draw_skeleton_on_blank(landmarks, connections, image_size, color=(255, 255, 255)):
    """
    Create a black image with a drawn pose skeleton.
    """
    blank_image = np.zeros((image_size[1], image_size[0], 3), dtype=np.uint8)
    drawing_spec = mp_drawing.DrawingSpec(color=color, thickness=10, circle_radius=3)
    
    mp_drawing.draw_landmarks(
        blank_image,
        landmarks,
        connections,
        landmark_drawing_spec=drawing_spec,
        connection_drawing_spec=drawing_spec
    )
    return blank_image

def compare_landmark_sets(landmarks1, landmarks2, visibility_threshold=0.5, tolerance=0.2, match_ratio_threshold=0.8):
    """
    Compare two lists of pose landmarks and return True if they are similar enough.
    """
    if landmarks1 is None or landmarks2 is None:
        return False

    matched = 0
    total = 0

    for i in range(len(landmarks1)):
        lm1 = landmarks1[i]
        lm2 = landmarks2[i]

        if lm1.visibility < visibility_threshold or lm2.visibility < visibility_threshold:
            continue

        distance = np.linalg.norm([lm1.x - lm2.x, lm1.y - lm2.y])

        if distance < tolerance:
            matched += 1
        total += 1

    if total == 0:
        return False

    match_ratio = matched / total
    return match_ratio >= match_ratio_threshold
