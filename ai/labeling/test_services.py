#!/usr/bin/env python3
"""
Test script for the updated labeling services with PostgreSQL and audiowaveform
"""
import sys
import os
import psycopg2

# Add the project root to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from ai.labeling import services

def test_database_connection():
    """Test the database connection"""
    print("Testing database connection...")
    try:
        conn = services.get_db_connection()
        if conn:
            print("[OK] Database connection successful")
            conn.close()
            return True
        else:
            print("[ERROR] Database connection failed")
            return False
    except Exception as e:
        print(f"[ERROR] Database connection error: {e}")
        return False

def test_get_audio_queue():
    """Test the get_audio_queue function"""
    print("\nTesting get_audio_queue...")
    try:
        queue = services.get_audio_queue()
        print(f"[OK] Queue retrieved successfully. Found {len(queue)} items")
        for i, item in enumerate(queue[:3]):  # Show first 3 items
            print(f"  {i+1}. ID: {item['id']}, File: {item['file_name']}, Processed: {item['is_processed']}")
        return True
    except Exception as e:
        print(f"[ERROR] Error retrieving queue: {e}")
        return False

def test_get_audio_file_path():
    """Test the get_audio_file_path function with a sample ID"""
    print("\nTesting get_audio_file_path...")
    try:
        # Use a sample ID - if queue has items, use the first one
        queue = services.get_audio_queue()
        if queue:
            sample_id = queue[0]['id']
            path, filename = services.get_audio_file_path(sample_id)
            if path and filename:
                print(f"[OK] Audio file path retrieved for ID {sample_id}: {os.path.join(path, filename)}")
                return True
            else:
                print(f"[ERROR] Could not retrieve path for ID {sample_id}")
                return False
        else:
            print("No items in queue to test with, using default ID 1")
            path, filename = services.get_audio_file_path(1)
            if path and filename:
                print(f"[OK] Audio file path retrieved for default ID: {os.path.join(path, filename)}")
                return True
            else:
                print("[ERROR] Could not retrieve path for default ID")
                return False
    except Exception as e:
        print(f"[ERROR] Error retrieving audio file path: {e}")
        return False

def test_generate_or_get_peaks():
    """Test the generate_or_get_peaks function"""
    print("\nTesting generate_or_get_peaks...")
    try:
        # Use a sample ID - if queue has items, use the first one
        queue = services.get_audio_queue()
        if queue:
            sample_id = queue[0]['id']
            peaks_path, peaks_filename = services.generate_or_get_peaks(sample_id)
            if peaks_path and peaks_filename:
                print(f"[OK] Peaks data retrieved/generated for ID {sample_id}: {os.path.join(peaks_path, peaks_filename)}")
                return True
            else:
                print(f"[ERROR] Could not retrieve/generate peaks for ID {sample_id}")
                return False
        else:
            print("No items in queue to test with, using default ID 1")
            peaks_path, peaks_filename = services.generate_or_get_peaks(1)
            if peaks_path and peaks_filename:
                print(f"[OK] Peaks data retrieved/generated for default ID: {os.path.join(peaks_path, peaks_filename)}")
                return True
            else:
                print("[ERROR] Could not retrieve/generate peaks for default ID")
                return False
    except Exception as e:
        print(f"[ERROR] Error generating/getting peaks: {e}")
        return False

def test_save_label_data():
    """Test the save_label_data function with sample data"""
    print("\nTesting save_label_data...")
    try:
        # Use a sample ID - if queue has items, use the first one
        queue = services.get_audio_queue()
        if queue:
            sample_id = queue[0]['id']
            sample_data = {
                "label": "normal",
                "confidence": 95,
                "annotations": [
                    {
                        "time_start": 0.1,
                        "time_end": 0.5,
                        "freq_min": 100,
                        "freq_max": 500,
                        "label": "normal"
                    }
                ]
            }
            success, message = services.save_label_data(sample_id, 1, sample_data)
            if success:
                print(f"[OK] Label data saved successfully for ID {sample_id}")
                return True
            else:
                print(f"[ERROR] Could not save label data for ID {sample_id}: {message}")
                return False
        else:
            print("No items in queue to test with")
            return False
    except Exception as e:
        print(f"[ERROR] Error saving label data: {e}")
        return False

def main():
    """Main test function"""
    print("Starting tests for labeling services...")
    print(f"Audio base path: {services.AUDIO_BASE_PATH}")
    print(f"Peaks cache path: {services.PEAKS_CACHE_PATH}")
    
    test_results = []
    
    # Run each test
    test_results.append(test_database_connection())
    test_results.append(test_get_audio_queue())
    test_results.append(test_get_audio_file_path())
    test_results.append(test_generate_or_get_peaks())
    test_results.append(test_save_label_data())
    
    # Summary
    passed = sum(test_results)
    total = len(test_results)
    print(f"\nTest Summary: {passed}/{total} tests passed")
    
    if passed == total:
        print("[SUCCESS] All tests passed!")
        return True
    else:
        print("[ERROR] Some tests failed")
        return False

if __name__ == "__main__":
    main()