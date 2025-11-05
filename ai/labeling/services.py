import os
import subprocess

# This would typically come from a config file or environment variables
AUDIO_BASE_PATH = 'C:\\Users\\gmdqn\\signalcraft\\data\\labeling_ready'
PEAKS_CACHE_PATH = 'C:\\Users\\gmdqn\\signalcraft\\data\\peaks_cache'

# A dummy mapping from file ID to an actual file name
# In a real implementation, this would be a database lookup.
DUMMY_FILE_DB = {
    101: "labeling_normal_2025-09-29T12-21-02-244Z_1.wav",
    102: "labeling_normal_2025-09-29T12-21-02-244Z_2.wav",
}

def get_audio_queue():
    """
    Fetches a list of audio files that need labeling.
    TODO: Replace this with actual database query logic.
    """
    queue = []
    for file_id, file_name in DUMMY_FILE_DB.items():
        queue.append({
            "id": file_id,
            "file_name": file_name,
            "url": f"/api/labeling/audio/{file_id}",
            "peaks_url": f"/api/labeling/peaks/{file_id}",
            "is_processed": False # Assuming all in this dummy queue are unprocessed
        })
    return queue

def get_audio_file_path(file_id):
    """
    Retrieves the full path and filename for a given audio file ID.
    TODO: Replace this with a database lookup.
    """
    filename = DUMMY_FILE_DB.get(file_id)
    if not filename:
        return None, None
    
    # Return directory and filename separately for send_from_directory
    return AUDIO_BASE_PATH, filename

def generate_or_get_peaks(file_id):
    """
    Generates peaks data using audiowaveform if it doesn't exist,
    otherwise returns the path to the cached file.
    """
    audio_dir, audio_filename = get_audio_file_path(file_id)
    if not audio_dir:
        return None, None

    audio_filepath = os.path.join(audio_dir, audio_filename)
    
    # Define the path for the peaks file
    peaks_filename = f"{os.path.splitext(audio_filename)[0]}.json"
    peaks_filepath = os.path.join(PEAKS_CACHE_PATH, peaks_filename)

    # Create cache directory if it doesn't exist
    os.makedirs(PEAKS_CACHE_PATH, exist_ok=True)

    if not os.path.exists(peaks_filepath):
        print(f"--- PEAKS FILE NOT FOUND for {audio_filename} ---")
        try:
            # Simulate running audiowaveform
            # In a real scenario, you would run the actual command:
            # cmd = [
            #     'audiowaveform',
            #     '-i', audio_filepath,
            #     '-o', peaks_filepath,
            #     '--pixels-per-second', '100', # Example options
            #     '--bits', '8'
            # ]
            # print(f"Running command: {' '.join(cmd)}")
            # subprocess.run(cmd, check=True, capture_output=True, text=True)

            # For this dummy implementation, we'll just create an empty json file
            print(f"SIMULATING: audiowaveform -i {audio_filepath} -o {peaks_filepath}")
            with open(peaks_filepath, 'w') as f:
                f.write('{"version": 2, "channels": 1, "data": []}') # Write minimal valid json
            print(f"--- DUMMY PEAKS FILE CREATED: {peaks_filepath} ---")

        except Exception as e:
            print(f"Error running audiowaveform (simulation): {e}")
            return None, None

    return PEAKS_CACHE_PATH, peaks_filename

def save_label_data(file_id, labeler_id, data):
    """
    Saves the submitted labeling data.
    TODO: Replace this with actual database insertion logic.
    """
    print("--- SAVING LABEL DATA ---")
    print(f"File ID: {file_id}")
    print(f"Labeler ID: {labeler_id}")
    print(f"Data Received: {data}")
    print("--- SIMULATED SAVE COMPLETE ---")
    
    # In a real implementation, you would perform DB operations here.
    # If successful:
    return True, "Labeling data saved successfully."
    # If failed:
    # return False, "Failed to save to database."