import base64
import cv2
import numpy as np
import mediapipe as mp
from app.pose_analyzer import detect_pose

mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils

def is_landmark_valid(lm, margin=0.05):
    """
    Returns True if the landmark is visible and within frame margins.
    """
    return (lm.visibility > 0.5 and margin < lm.x < 1 - margin and margin < lm.y < 1 - margin)


def process_uploaded_image(image_base64):
    """
    Decodes the image, runs pose estimation, and returns analysis results.
    """
    try:
        nparr = np.frombuffer(base64.b64decode(image_base64), np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    except Exception:
        return {'error': 'Failed to decode image'}

    if image is None:
        return {'error': 'Empty or unreadable image'}

    height, width, _ = image.shape
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    with mp_pose.Pose(static_image_mode=True) as pose:
        results = pose.process(image_rgb)

    if not results.pose_landmarks:
        return {'message': 'No pose detected'}

    landmarks = results.pose_landmarks.landmark
    important_ids = [
        mp_pose.PoseLandmark.NOSE.value,
        mp_pose.PoseLandmark.LEFT_SHOULDER.value,
        mp_pose.PoseLandmark.RIGHT_SHOULDER.value,
        mp_pose.PoseLandmark.LEFT_ELBOW.value,
        mp_pose.PoseLandmark.RIGHT_ELBOW.value,
        mp_pose.PoseLandmark.LEFT_WRIST.value,
        mp_pose.PoseLandmark.RIGHT_WRIST.value,
        mp_pose.PoseLandmark.LEFT_HIP.value,
        mp_pose.PoseLandmark.RIGHT_HIP.value,
        mp_pose.PoseLandmark.LEFT_KNEE.value,
        mp_pose.PoseLandmark.RIGHT_KNEE.value,
        mp_pose.PoseLandmark.LEFT_ANKLE.value,
        mp_pose.PoseLandmark.RIGHT_ANKLE.value,
    ]

    if not all(is_landmark_valid(landmarks[i]) for i in important_ids):
        return {'message': 'The full body is not fully visible in the image'}

    # Optionally save image with skeleton
    mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
    cv2.imwrite("pose_result.png", image)

    landmarks_data = [
        {
            "id": i,
            "x": lm.x,
            "y": lm.y,
            "z": lm.z,
            "visibility": lm.visibility
        }
        for i, lm in enumerate(landmarks)
    ]

    pose_name = detect_pose(landmarks)

    return {
    'message': f"Pose detected: {pose_name}" if pose_name else "Pose detected but unrecognized",
    'pose': pose_name,
    'landmarks': landmarks_data
    }
