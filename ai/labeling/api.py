
from flask import Blueprint, jsonify, request, g, send_from_directory
from functools import wraps

def require_labeler(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # In a real-world scenario, these headers are passed by the gateway/reverse proxy
        # after the Node.js authentication service has validated the user.
        user_id = request.headers.get('X-User-ID')
        user_role = request.headers.get('X-User-Role')

        if not user_id or not user_role:
            return jsonify({"error": "Authentication headers missing"}), 401

        if user_role not in ['labeler', 'admin']:
            return jsonify({"error": "Permission denied. Labeler or admin role required."}), 403

        g.user_id = user_id
        g.user_role = user_role
        return f(*args, **kwargs)
    return decorated_function

# Define the blueprint
labeling_bp = Blueprint(
    'labeling_bp',
    __name__,
    template_folder='templates',
    static_folder='static'
)

from ai.labeling import services

@labeling_bp.route('/ping', methods=['GET'])
@require_labeler
def ping():
    """A simple route to check if the blueprint is registered and working."""
    return jsonify({
        "status": "ok", 
        "message": "Labeling API is alive!",
        "current_user_id": g.user_id,
        "current_user_role": g.user_role
    }), 200

@labeling_bp.route('/queue', methods=['GET'])
@require_labeler
def get_labeling_queue():
    """Returns a list of audio files waiting to be labeled."""
    # The actual logic will be in the services.py file
    queue_items = services.get_audio_queue()
    return jsonify(queue_items), 200

@labeling_bp.route('/audio/<int:file_id>', methods=['GET'])
@require_labeler
def get_audio_file(file_id):
    """Serves the raw audio file."""
    # The service function will handle finding the file path
    # and this route will handle serving it.
    file_path, filename = services.get_audio_file_path(file_id)
    if not file_path:
        return jsonify({"error": "Audio file not found"}), 404
    return send_from_directory(file_path, filename)

@labeling_bp.route('/peaks/<int:file_id>', methods=['GET'])
@require_labeler
def get_peaks_data(file_id):
    """Generates (if needed) and serves the peaks.json data."""
    peaks_json_path, filename = services.generate_or_get_peaks(file_id)
    if not peaks_json_path:
        return jsonify({"error": "Could not generate or find peaks data"}), 500
    return send_from_directory(peaks_json_path, filename)

@labeling_bp.route('/upload', methods=['POST'])
@require_labeler
def upload_audio_file():
    """Uploads an audio file for labeling."""
    if 'audio_file' not in request.files:
        return jsonify({"error": "No audio file provided"}), 400
    
    file = request.files['audio_file']
    original_filename = request.form.get('original_filename', '')
    
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
    
    if file:
        try:
            # Import OS and other necessary modules
            import os
            from datetime import datetime
            
            # Define upload directory
            upload_dir = os.getenv('AUDIO_BASE_PATH', 'C:\\Users\\gmdqn\\signalcraft\\data\\labeling_ready')
            os.makedirs(upload_dir, exist_ok=True)
            
            # Create a standardized filename with a labeling prefix
            timestamp = datetime.now().strftime("%Y-%m-%dT%H-%M-%S-%fZ")[:-3]  # Include milliseconds
            name, ext = os.path.splitext(file.filename)
            # If original file already has "labeling_" prefix, keep it, otherwise create a generic one
            if not original_filename.startswith('labeling_'):
                new_filename = f"labeling_unknown_{timestamp}{ext}"
            else:
                new_filename = f"{original_filename.split('.')[0]}_{timestamp}{ext}"
            
            file_path = os.path.join(upload_dir, new_filename)
            file.save(file_path)
            
            # Get file stats
            file_size = os.path.getsize(file_path)
            
            # Register the file in the database using the services module
            # We'll add a new function in services for this purpose
            file_registered = services.register_uploaded_file(
                filename=new_filename,
                file_path=file_path,
                file_size=file_size,
                uploaded_by=g.user_id
            )
            
            if file_registered:
                return jsonify({
                    "message": "File uploaded successfully",
                    "filename": new_filename,
                    "file_path": file_path
                }), 200
            else:
                return jsonify({"error": "Failed to register file in database"}), 500
                
        except Exception as e:
            print(f"Error uploading file: {e}")
            return jsonify({"error": str(e)}), 500

@labeling_bp.route('/save', methods=['POST'])
@require_labeler
def save_label():
    """Saves the labeling data for a given audio file."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid JSON payload"}), 400

    file_id = data.get('audio_file_id')
    if not file_id:
        return jsonify({"error": "audio_file_id is missing"}), 400

    # Pass the data to the service layer for processing
    success, message = services.save_label_data(
        file_id=file_id,
        labeler_id=g.user_id, 
        data=data
    )

    if success:
        return jsonify({"message": message}), 200
    else:
        return jsonify({"error": message}), 500
