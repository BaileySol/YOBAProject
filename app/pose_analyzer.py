import numpy as np
import mediapipe as mp

mp_pose = mp.solutions.pose

def calculate_angle(pointA, pointB, pointC):
    """
    Calculate angle (in degrees) between three points
    """
    a = np.array(pointA)
    b = np.array(pointB)
    c = np.array(pointC)

    ba = a - b
    bc = c - b

    cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
    angle = np.arccos(np.clip(cosine_angle, -1.0, 1.0))

    return np.degrees(angle)

def detect_tree_pose(landmarks):
    """
    Check for each pose individually based on landmark coordinates
    """
    left_knee_angle = calculate_angle(
        (landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x, landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y),
        (landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].x, landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].y),
        (landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].x, landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].y)
    )

    hands_above_head = (
        landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y < landmarks[mp_pose.PoseLandmark.NOSE.value].y and
        landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].y < landmarks[mp_pose.PoseLandmark.NOSE.value].y
    )

    return left_knee_angle > 100 and hands_above_head

def detect_plank_pose(landmarks):
    shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value]
    hip = landmarks[mp_pose.PoseLandmark.LEFT_HIP.value]
    ankle = landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value]

    body_angle = calculate_angle((shoulder.x, shoulder.y), (hip.x, hip.y), (ankle.x, ankle.y))
    return 160 < body_angle < 180

def detect_boat_pose(landmarks):
    left_knee = landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value]
    left_hip = landmarks[mp_pose.PoseLandmark.LEFT_HIP.value]
    left_ankle = landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value]

    knee_angle = calculate_angle((left_hip.x, left_hip.y), (left_knee.x, left_knee.y), (left_ankle.x, left_ankle.y))

    hands_up = landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y < landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y

    return 130 < knee_angle < 160 and hands_up

def detect_triangle_pose(landmarks):
    left_shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value]
    left_hip = landmarks[mp_pose.PoseLandmark.LEFT_HIP.value]
    left_ankle = landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value]

    angle = calculate_angle((left_shoulder.x, left_shoulder.y), (left_hip.x, left_hip.y), (left_ankle.x, left_ankle.y))

    one_hand_up = landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y < landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y

    return 50 < angle < 80 and one_hand_up

def detect_standing_pose(landmarks):
    left_shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value]
    left_hip = landmarks[mp_pose.PoseLandmark.LEFT_HIP.value]
    left_ankle = landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value]

    angle = calculate_angle((left_shoulder.x, left_shoulder.y), (left_hip.x, left_hip.y), (left_ankle.x, left_ankle.y))

    feet_together = abs(
        landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].x -
        landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].x
    ) < 0.05

    hands_at_sides = (
        abs(landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y - landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y) < 0.1 and
        abs(landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].y - landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].y) < 0.1
    )

    return 170 < angle < 180 and feet_together and hands_at_sides

def detect_pose(landmarks):
    """
    Master function that returns the name of the pose or None
    """
    if detect_standing_pose(landmarks):
        return "tadasana"
    elif detect_tree_pose(landmarks):
        return "tree"
    elif detect_plank_pose(landmarks):
        return "plank"
    elif detect_boat_pose(landmarks):
        return "boat"
    elif detect_triangle_pose(landmarks):
        return "triangle"
    return None
