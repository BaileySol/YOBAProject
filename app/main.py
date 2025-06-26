import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask_cors import CORS
from services import image_pose_service
from instruction_repository import get_instructions

from flask import Flask, request, jsonify, send_from_directory
app = Flask(__name__, static_folder='static')
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

@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/static/<path:filename>')
def serve_static(filename):
    """
    Serves static files from the 'static' directory.
    """
    return send_from_directory(app.static_folder, filename)

if __name__ == '__main__':
    app.run(port=5000, debug=True)
