import os
import subprocess
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
import json

# Load environment variables from .env file
load_dotenv()

# Database configuration from environment variables
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', 5432)
DB_NAME = os.getenv('DB_NAME', 'smartcompressor_ai')
DB_USER = os.getenv('DB_USER', 'postgres')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'signalcraft6898')

# Audio file paths
AUDIO_BASE_PATH = os.getenv('AUDIO_BASE_PATH', 'C:\\Users\\gmdqn\\signalcraft\\data\\labeling_ready')
PEAKS_CACHE_PATH = os.getenv('PEAKS_CACHE_PATH', 'C:\\Users\\gmdqn\\signalcraft\\data\\peaks_cache')


def get_db_connection():
    """Creates a connection to the PostgreSQL database."""
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        return conn
    except psycopg2.Error as e:
        print(f"Database connection error: {e}")
        return None


def get_audio_queue():
    """
    Fetches a list of audio files that need labeling from the database.
    """
    conn = get_db_connection()
    if not conn:
        return []
    
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            # We select audio files that don't have corresponding labels yet
            query = """
                SELECT 
                    af.id,
                    af.file_name,
                    COALESCE(l.id IS NOT NULL, false) as is_processed
                FROM audio_files af
                LEFT JOIN labels l ON af.file_name = l.file_name
                WHERE af.file_name LIKE 'labeling_%'
                ORDER BY af.upload_timestamp DESC
            """
            cursor.execute(query)
            results = cursor.fetchall()
        
        queue = []
        for row in results:
            queue.append({
                "id": row['id'],
                "file_name": row['file_name'],
                "url": f"/api/labeling/audio/{row['id']}",  # This endpoint needs to be implemented
                "peaks_url": f"/api/labeling/peaks/{row['id']}",  # This endpoint needs to be implemented
                "is_processed": bool(row['is_processed'])
            })
        
        return queue
    except psycopg2.Error as e:
        print(f"Database query error: {e}")
        return []
    finally:
        conn.close()


def get_audio_file_path(file_id):
    """
    Retrieves the full path and filename for a given audio file ID from the database.
    """
    conn = get_db_connection()
    if not conn:
        return None, None
    
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            query = "SELECT file_name, file_path FROM audio_files WHERE id = %s"
            cursor.execute(query, (file_id,))
            result = cursor.fetchone()
        
        if result:
            # Use the file_path from the database, or construct from base path if not available
            file_path = result['file_path'] if result['file_path'] else os.path.join(AUDIO_BASE_PATH, result['file_name'])
            # Extract directory and filename
            directory, filename = os.path.split(file_path)
            return directory, filename
        else:
            return None, None
    except psycopg2.Error as e:
        print(f"Database query error: {e}")
        return None, None
    finally:
        conn.close()


def generate_or_get_peaks(file_id):
    """
    Generates peaks data using audiowaveform if it doesn't exist,
    otherwise returns the path to the cached file.
    """
    audio_dir, audio_filename = get_audio_file_path(file_id)
    if not audio_dir or not audio_filename:
        print(f"Could not find audio file for ID: {file_id}")
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
            cmd = [
                'audiowaveform',
                '-i', audio_filepath,
                '-o', peaks_filepath,
                '--pixels-per-second', '100',  # Example option
                '--bits', '8'
            ]
            print(f"Running command: {' '.join(cmd)}")
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            print(f"--- PEAKS FILE CREATED: {peaks_filepath} ---")
            print(f"Command output: {result.stdout}")

        except subprocess.CalledProcessError as e:
            print(f"Error running audiowaveform: {e}")
            print(f"Command output (stderr): {e.stderr}")
            return None, None
        except FileNotFoundError:
            print("Error: audiowaveform command not found. Please install audiowaveform.")
            return None, None
        except Exception as e:
            print(f"Unexpected error running audiowaveform: {e}")
            return None, None

    return PEAKS_CACHE_PATH, peaks_filename


def register_uploaded_file(filename, file_path, file_size, uploaded_by=1):
    """
    Registers an uploaded audio file in the database.
    """
    conn = get_db_connection()
    if not conn:
        return False
    
    try:
        with conn.cursor() as cursor:
            # Check if file already exists
            cursor.execute("SELECT id FROM audio_files WHERE file_name = %s", (filename,))
            existing = cursor.fetchone()
            
            if existing:
                # File already exists, update it
                cursor.execute("""
                    UPDATE audio_files 
                    SET file_path = %s, file_size = %s, upload_timestamp = CURRENT_TIMESTAMP
                    WHERE file_name = %s
                """, (file_path, file_size, filename))
            else:
                # Insert new file
                # For uploaded files, we'll use default values for some fields
                # The user can update device_id, store_id, etc. later if needed
                cursor.execute("""
                    INSERT INTO audio_files (
                        user_id, file_name, file_path, file_size, 
                        upload_timestamp, is_processed
                    ) VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP, FALSE)
                """, (uploaded_by, filename, file_path, file_size))
            
            conn.commit()
            print(f"File {filename} registered in database")
            return True
    except psycopg2.Error as e:
        print(f"Database error registering file: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()


def save_label_data(file_id, labeler_id, data):
    """
    Saves the submitted labeling data to the database.
    """
    conn = get_db_connection()
    if not conn:
        return False, "Could not connect to database."
    
    try:
        with conn.cursor() as cursor:
            # First get the filename for the audio file ID
            cursor.execute("SELECT file_name FROM audio_files WHERE id = %s", (file_id,))
            result = cursor.fetchone()
            if not result:
                return False, "Audio file not found in database."
            
            file_name = result[0]
            
            # Insert or update label
            cursor.execute("""
                INSERT INTO labels (file_name, label, confidence, labeler_id, metadata)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (file_name) 
                DO UPDATE SET 
                    label = EXCLUDED.label,
                    confidence = EXCLUDED.confidence,
                    labeler_id = EXCLUDED.labeler_id,
                    metadata = EXCLUDED.metadata,
                    updated_at = CURRENT_TIMESTAMP
            """, (
                file_name,
                data.get('label'),
                data.get('confidence'),
                labeler_id,
                json.dumps(data.get('annotations', []))  # Store annotations as JSON
            ))
            
            conn.commit()
            print(f"Label saved for file ID {file_id}")
            return True, "Labeling data saved successfully."
    except psycopg2.Error as e:
        print(f"Database error saving label: {e}")
        conn.rollback()
        return False, f"Database error: {str(e)}"
    finally:
        conn.close()


def delete_audio_file(file_id, user_id):
    """
    Deletes an audio file and its associated data from the database and filesystem.
    """
    conn = get_db_connection()
    if not conn:
        return False, "Could not connect to database."
    
    try:
        with conn.cursor() as cursor:
            # Get file information before deletion
            cursor.execute("SELECT file_name, file_path FROM audio_files WHERE id = %s", (file_id,))
            result = cursor.fetchone()
            if not result:
                return False, "Audio file not found in database."
            
            file_name, file_path = result
            
            # Delete associated label data
            cursor.execute("DELETE FROM labels WHERE file_name = %s", (file_name,))
            
            # Delete the audio file record
            cursor.execute("DELETE FROM audio_files WHERE id = %s", (file_id,))
            
            conn.commit()
            
            # Delete the actual file from the filesystem if it exists
            if file_path and os.path.exists(file_path):
                os.remove(file_path)
                print(f"File {file_path} deleted from filesystem")
            
            # Also delete associated peaks file if it exists
            peaks_filename = f"{os.path.splitext(file_name)[0]}.json"
            peaks_filepath = os.path.join(PEAKS_CACHE_PATH, peaks_filename)
            if os.path.exists(peaks_filepath):
                os.remove(peaks_filepath)
                print(f"Peaks file {peaks_filepath} deleted from filesystem")
            
            print(f"File ID {file_id} deleted from database")
            return True, "Audio file and associated data deleted successfully."
    except psycopg2.Error as e:
        print(f"Database error deleting file: {e}")
        conn.rollback()
        return False, f"Database error: {str(e)}"
    except Exception as e:
        print(f"Error deleting file from filesystem: {e}")
        conn.rollback()
        return False, f"Filesystem error: {str(e)}"
    finally:
        conn.close()