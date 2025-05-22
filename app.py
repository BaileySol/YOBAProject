from flask import Flask, request, jsonify
from flask_cors import CORS
import base64
import cv2
import numpy as np
import mediapipe as mp

app = Flask(__name__)
CORS(app)

mp_pose = mp.solutions.pose
pose = mp_pose.Pose(static_image_mode=True)
mp_drawing = mp.solutions.drawing_utils

@app.route('/upload', methods=['POST'])
def upload_image():
    data = request.json
    image_data = data['image'].split(',')[1]  # להסיר את "data:image/png;base64,"

    # המרת base64 ל־OpenCV image
    nparr = np.frombuffer(base64.b64decode(image_data), np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    if image is None:
        return jsonify({'error': 'Image decode failed'}), 400

    height, width, _ = image.shape

    # המרת צבעים ל-RGB (MediaPipe דורש RGB)
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # ניתוח שלד
    results = pose.process(image_rgb)

    if results.pose_landmarks:
        landmarks = results.pose_landmarks.landmark

        def is_point_valid(lm):
            margin = 0.05
            return (lm.visibility > 0.5 and
                    margin < lm.x < 1 - margin and
                    margin < lm.y < 1 - margin)

        important_landmarks_ids = [
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

        all_valid = all(is_point_valid(landmarks[i]) for i in important_landmarks_ids)

        if not all_valid:
            return jsonify({'message': 'The full body is not fully visible in the image'}), 200

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

        return jsonify({'message': 'Pose detected', 'landmarks': landmarks_data})
    else:
        return jsonify({'message': 'No pose detected'}), 200

if __name__ == '__main__':
    app.run(port=5000, debug=True)
