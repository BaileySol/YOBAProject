"""
This script is intended for internal development and testing only.

✔ Use this file to test live yoga pose detection using your local webcam.
✔ It allows real-time evaluation of pose recognition logic without the need for a web interface.
✔ Useful for verifying accuracy of pose algorithms and demonstrating functionality to your advisor.
✔ Not connected to the actual client-server web application.
✔ Not intended for production or deployment in the final user-facing system.

Run locally on your machine for fast and easy development iteration.
"""

import cv2
import mediapipe as mp
from pose_analyzer import detect_pose

# Initialize MediaPipe pose estimation
mp_pose = mp.solutions.pose
pose_detector = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)
mp_drawing = mp.solutions.drawing_utils

# Start video capture from webcam
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Could not open webcam.")
    exit()

print("Starting live pose detection. Press 'q' to quit.")

while True:
    ret, frame = cap.read()
    if not ret:
        print("Error: Failed to capture frame.")
        break

    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = pose_detector.process(rgb_frame)

    pose_name = None

    if results.pose_landmarks:
        mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

        pose_name = detect_pose(results.pose_landmarks.landmark)

        if pose_name:
            cv2.putText(frame, f"{pose_name.upper()} detected", (30, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 3)
        else:
            cv2.putText(frame, "Unknown pose", (30, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 3)

    else:
        cv2.putText(frame, "No pose detected", (30, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 3)

    cv2.imshow("YOBA Pose Detection", frame)

    if cv2.waitKey(10) & 0xFF == ord('q'):
        print("Quitting.")
        break

cap.release()
cv2.destroyAllWindows()
