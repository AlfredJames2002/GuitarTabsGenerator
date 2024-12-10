import subprocess
import os
import demucs

def validate_file_path(file_path):
    
    #Check if the file path is valid and if the file exists.
    if not os.path.isfile(file_path):
        print(f"Error: The file '{file_path}' does not exist.")
        return False
    elif not file_path.lower().endswith('.mp3'):
        print("Error: The file is not an MP3. Please provide a valid MP3 file.")
        return False
    print("File path is valid. hold on a minute")
    return True

def run_demucs(input_file):
    
    #Run Demucs to isolate stems from the provided MP3 file.
    try:
        command = ["demucs", input_file]
        subprocess.run(command, check=True)
        print("Separation completed successfully.")
    except subprocess.CalledProcessError:
        print("Error: Demucs encountered an issue. Please ensure Demucs is installed correctly.")
        return False
    return True