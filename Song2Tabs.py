import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import shutil
import numpy as np
import simpleaudio as sa
from source_seperator import validate_file_path, run_demucs
from note_detector import load_song
from tab_generator import main as generate_tabs

# Global variables
audio_file = None
separated_file = None
output_file = "guitar_tabs.txt"
tabs_content = ""
play_obj = None
separated_dir = None


def toggle_buttons(state):
    """Enable or disable all buttons based on state."""
    upload_button.config(state=state)
    separate_button.config(state=state)
    detect_button.config(state=state)
    generate_button.config(state=state)
    root.update_idletasks()


def upload_file():
    global audio_file
    file_path = filedialog.askopenfilename(filetypes=[("Audio Files", "*.mp3 *.wav")])
    if file_path:
        audio_file = file_path
        file_label.config(text=f"File Selected: {file_path}")
    else:
        messagebox.showerror("Error", "No file selected!")


def separate_audio():
    global audio_file, separated_file, separated_dir
    if not audio_file:
        messagebox.showerror("Error", "No audio file selected!")
        return

    toggle_buttons("disabled")
    progress_panel.config(state="normal")
    progress_panel.insert(tk.END, "Starting audio separation...\n")
    progress_panel.see(tk.END)
    progress_panel.config(state="disabled")

    if run_demucs(audio_file):
        separated_dir = os.path.join("separated", "htdemucs", os.path.basename(audio_file).replace(".mp3", ""))
        separated_file = os.path.join(separated_dir, "other.wav")
        if os.path.exists(separated_file):
            progress_panel.config(state="normal")
            progress_panel.insert(tk.END, "Audio separation completed successfully!\n")
            progress_panel.see(tk.END)
            progress_panel.config(state="disabled")
            update_separated_file_tab()
        else:
            messagebox.showerror("Error", "'other.wav' not found after separation!")
    else:
        messagebox.showerror("Error", "Audio separation failed!")

    toggle_buttons("normal")


def update_separated_file_tab():
    """Update the separated file tab with playback controls."""
    separated_panel.config(state="normal")
    separated_panel.delete(1.0, tk.END)
    separated_panel.insert(tk.END, f"Separated File: {separated_file}\n")
    separated_panel.config(state="disabled")


def play_audio():
    global play_obj, separated_file
    if separated_file:
        try:
            wave_obj = sa.WaveObject.from_wave_file(separated_file)
            play_obj = wave_obj.play()
        except Exception as e:
            messagebox.showerror("Error", f"Could not play audio: {e}")


def stop_audio():
    global play_obj
    if play_obj:
        play_obj.stop()


def pause_audio():
    global play_obj
    if play_obj and play_obj.is_playing():
        play_obj.stop()


def detect_notes():
    global audio_file
    if not audio_file:
        messagebox.showerror("Error", "No audio file selected!")
        return

    toggle_buttons("disabled")

    progress_panel.config(state="normal")
    progress_panel.insert(tk.END, "Detecting notes...\n")
    progress_panel.see(tk.END)
    progress_panel.config(state="disabled")

    try:
        note_values = load_song(audio_file)
        np.save("detected_notes.npy", note_values)
        progress_panel.config(state="normal")
        progress_panel.insert(tk.END, "Notes detected successfully and saved!\n")
        progress_panel.see(tk.END)
        progress_panel.config(state="disabled")
    except Exception as e:
        progress_panel.config(state="normal")
        progress_panel.insert(tk.END, f"Note detection failed: {e}\n")
        progress_panel.see(tk.END)
        progress_panel.config(state="disabled")

    toggle_buttons("normal")


def generate_tabs_file():
    global tabs_content
    toggle_buttons("disabled")

    progress_panel.config(state="normal")
    progress_panel.insert(tk.END, "Generating guitar tabs...\n")
    progress_panel.see(tk.END)
    progress_panel.config(state="disabled")

    try:
        # Load detected notes
        note_values = np.load("detected_notes.npy")

        # Define the standard tuning array
        standard = [
            ['E2', 'F2', 'F#2', 'G2', 'G#2', 'A2', 'A#2', 'B2', 'C3', 'C#3', 'D3', 'D#3'],
            ['A2', 'A#2', 'B2', 'C3', 'C#3', 'D3', 'D#3', 'E3', 'F3', 'F#3', 'G3', 'G#3'],
            ['D3', 'D#3', 'E3', 'F3', 'F#3', 'G3', 'G#3', 'A3', 'A#3', 'B3', 'C4', 'C#4'],
            ['G3', 'G#3', 'A3', 'A#3', 'B3', 'C4', 'C#4', 'D4', 'D#4', 'E4', 'F4', 'F#4'],
            ['B3', 'C4', 'C#4', 'D4', 'D#4', 'E4', 'F4', 'F#4', 'G4', 'G#4', 'A4', 'A#4'],
            ['E4', 'F4', 'F#4', 'G4', 'G#4', 'A4', 'A#4', 'B4', 'C5', 'C#5', 'D5', 'D#5'],
        ]

        # Generate the tabs and save to file
        tabs = generate_tabs(note_values, standard, output_filename=output_file)
        display_tabs(tabs)

        progress_panel.config(state="normal")
        progress_panel.insert(tk.END, f"Guitar tabs saved to {output_file}!\n")
        progress_panel.see(tk.END)
        progress_panel.config(state="disabled")
    except Exception as e:
        progress_panel.config(state="normal")
        progress_panel.insert(tk.END, f"Tab generation failed: {e}\n")
        progress_panel.see(tk.END)
        progress_panel.config(state="disabled")

    toggle_buttons("normal")


def display_tabs(tabs):
    global tabs_content
    tabs_content = "\n".join(tabs)
    tab_output_panel.config(state="normal")
    tab_output_panel.delete(1.0, tk.END)
    tab_output_panel.insert(tk.END, tabs_content)
    tab_output_panel.config(state="disabled")


def delete_separated_files():
    """Delete separated files and directory."""
    global separated_dir
    if separated_dir and os.path.exists(separated_dir):
        shutil.rmtree(separated_dir)
        print("Deleted separated audio directory.")

def delete_detected_notes():
    """Delete the detected notes file if it exists."""
    detected_notes_path = "detected_notes.npy"
    if os.path.exists(detected_notes_path):
        os.remove(detected_notes_path)
        print("Deleted detected_notes.npy.")

def on_closing():
    """Handle app closing."""
    delete_separated_files()
    delete_detected_notes()
    root.destroy()

# Tkinter UI Setup
root = tk.Tk()
root.title("Guitar Tab Generator")
root.geometry("900x700")

# Create tabs
notebook = ttk.Notebook(root)
notebook.pack(fill="both", expand=True)

# File Selection Tab
file_tab = ttk.Frame(notebook)
notebook.add(file_tab, text="File Selection")

file_label = tk.Label(file_tab, text="No file selected", font=("Arial", 12))
file_label.pack(pady=10)

upload_button = tk.Button(file_tab, text="Upload MP3 or WAV", command=upload_file)
upload_button.pack(pady=10)

separate_button = tk.Button(file_tab, text="Separate Audio", command=separate_audio)
separate_button.pack(pady=10)

# Separated File Tab
separated_tab = ttk.Frame(notebook)
notebook.add(separated_tab, text="Separated File")

separated_panel = tk.Text(separated_tab, height=10, wrap="word", state="disabled")
separated_panel.pack(fill="both", expand=True, padx=10, pady=10)

separated_play_button = tk.Button(separated_tab, text="Play", command=play_audio)
separated_play_button.pack(side="left", padx=5, pady=5)

separated_pause_button = tk.Button(separated_tab, text="Pause", command=pause_audio)
separated_pause_button.pack(side="left", padx=5, pady=5)

separated_stop_button = tk.Button(separated_tab, text="Stop", command=stop_audio)
separated_stop_button.pack(side="left", padx=5, pady=5)

# Progress Tab
progress_tab = ttk.Frame(notebook)
notebook.add(progress_tab, text="Actions")

progress_panel = tk.Text(progress_tab, height=20, state="disabled", wrap="word")
progress_panel.pack(fill="both", expand=True, padx=10, pady=10)

# Tab Generation Tab
tabs_tab = ttk.Frame(notebook)
notebook.add(tabs_tab, text="Generated Tabs")

tab_output_panel = tk.Text(tabs_tab, height=20, wrap="word", state="normal")
tab_output_panel.pack(fill="both", expand=True, padx=10, pady=10)

detect_button = tk.Button(progress_tab, text="Detect Notes", command=detect_notes)
detect_button.pack(pady=10)

generate_button = tk.Button(progress_tab, text="Generate Tabs", command=generate_tabs_file)
generate_button.pack(pady=20)

# Handle app closing
root.protocol("WM_DELETE_WINDOW", on_closing)

root.mainloop()