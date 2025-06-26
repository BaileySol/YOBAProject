import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, request, jsonify
from flask_cors import CORS
from services import image_pose_service
from instruction_repository import get_instructions

app = Flask(__name__)
CORS(app)  # Enable CORS for cross-origin access


@app.route('/upload', methods=['POST'])
def handle_image_upload():
    """
    Receives a base64-encoded image, decodes it,
    and returns the detected pose landmarks or an error message.
    """
    try:
        data = request.get_json()
        image_base64 = data.get('image', '').split(',')[1]
    except Exception:
        return jsonify({'error': 'Invalid image format'}), 400

    result = image_pose_service.process_uploaded_image(image_base64)
    return jsonify(result)


@app.route('/instructions/<pose_name>', methods=['GET'])
def handle_get_instructions(pose_name):
    """
    Given a pose name, returns the corresponding step-by-step instructions.
    """
    instructions = get_instructions(pose_name)
    if instructions:
        return jsonify({'instructions': instructions})
    else:
        return jsonify({'error': 'Pose not recognized'}), 404


if __name__ == '__main__':
    app.run(port=5000, debug=True)
