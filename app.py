from flask import Flask, request, jsonify
from flask_cors import CORS
from pose_instructions import pose_instructions_dict  # Dictionary with pose names and detailed instructions
import base64
import cv2
import numpy as np
import mediapipe as mp

# Initialize the Flask app
app = Flask(__name__)
CORS(app)  # Allow cross-origin requests (for frontend connection)

# Initialize MediaPipe pose estimation
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(static_image_mode=True)  # Static image mode is suitable for single-frame analysis
mp_drawing = mp.solutions.drawing_utils  # Utility for drawing pose landmarks on image


@app.route('/upload', methods=['POST'])
def upload_image():
    """
    Receive an image from the client, decode it, analyze the human pose using MediaPipe,
    and return detected pose landmarks or an error message.
    """
    data = request.json
    image_data = data['image'].split(',')[1]  # Remove the "data:image/png;base64," prefix

    # Convert base64 string to OpenCV image (numpy array)
    nparr = np.frombuffer(base64.b64decode(image_data), np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    if image is None:
        return jsonify({'error': 'Image decode failed'}), 400

    height, width, _ = image.shape

    # Convert BGR to RGB for MediaPipe processing
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # Run pose detection
    results = pose.process(image_rgb)

    if results.pose_landmarks:
        landmarks = results.pose_landmarks.landmark

        def is_point_valid(lm):
            """
            Check if a landmark is visible and within image boundaries (with margin).
            """
            margin = 0.05
            return (lm.visibility > 0.5 and margin < lm.x < 1 - margin and margin < lm.y < 1 - margin)
        
        # Important body landmarks to validate visibility
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

        # Verify that all important points are visible and inside the frame
        all_valid = all(is_point_valid(landmarks[i]) for i in important_landmarks_ids)

        if not all_valid:
            return jsonify({'message': 'The full body is not fully visible in the image'}), 200

        # Optionally draw the landmarks on the image and save to file
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
    

@app.route('/instructions/<pose_name>', methods=['GET'])
def get_instructions(pose_name):
    """
    Given a pose name (from the URL), return the corresponding list of instructions.
    """
    instructions = pose_instructions_dict.get(pose_name.lower())
    if instructions:
        return jsonify({'instructions': instructions})
    else:
        return jsonify({'error': 'Pose not recognized'}), 404

# Run the Flask server on port 5000
if __name__ == '__main__':
    app.run(port=5000, debug=True)
