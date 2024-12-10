import numpy as np
from itertools import product, combinations

# Initialize the 2D array for standard tuning with 6 strings and 12 columns(11 frets including open) 
standard = np.array([
    ['E2', 'F2', 'F#2', 'G2', 'G#2', 'A2', 'A#2', 'B2', 'C3', 'C#3', 'D3', 'D#3'],  # Low E
    ['A2', 'A#2', 'B2', 'C3', 'C#3', 'D3', 'D#3', 'E3', 'F3', 'F#3', 'G3', 'G#3'],  # A
    ['D3', 'D#3', 'E3', 'F3', 'F#3', 'G3', 'G#3', 'A3', 'A#3', 'B3', 'C4', 'C#4'],  # D
    ['G3', 'G#3', 'A3', 'A#3', 'B3', 'C4', 'C#4', 'D4', 'D#4', 'E4', 'F4', 'F#4'],  # G
    ['B3', 'C4', 'C#4', 'D4', 'D#4', 'E4', 'F4', 'F#4', 'G4', 'G#4', 'A4', 'A#4'],  # B
    ['E4', 'F4', 'F#4', 'G4', 'G#4', 'A4', 'A#4', 'B4', 'C5', 'C#5', 'D5', 'D#5']   # High e
])

def map_notes_to_fretboard(notes, standard):
    note_positions = {}
    for note in notes:
        positions = []
        for string_index, string in enumerate(standard):
            if note in string:
                fret = list(string).index(note)
                positions.append((string_index, fret))
        print(f"Note: {note}, Positions: {positions}")  # Debug
        note_positions[note] = sorted(positions, key=lambda x: x[1])  # Sort by fret
    return note_positions

def filter_positions_by_fret_range(note_positions, max_fret_range=3):
    from itertools import product
    all_combinations = list(product(*note_positions.values()))
    valid_combinations = []
    for combination in all_combinations:
        frets = [pos[1] for pos in combination if pos[1] != 0]
        if not frets or (max(frets) - min(frets) <= max_fret_range):
            valid_combinations.append(combination)

    if not valid_combinations:
        print("No valid combinations found in 3-fret range. Expanding to 4-fret range...")
        for combination in all_combinations:
            frets = [pos[1] for pos in combination if pos[1] != 0]
            if not frets or (max(frets) - min(frets) <= 4):  # Expand range
                valid_combinations.append(combination)

    valid_combinations = sorted(valid_combinations, key=lambda combo: sum(pos[1] for pos in combo))
    return valid_combinations if valid_combinations else []

def process_onsets(note_values, standard):
    # Filter out notes not in the fretboard range
    valid_notes = [note for note in note_values[:, 0] if any(note in string for string in standard)]

    # Continue processing only valid notes
    onset_groups = {}
    for note, onset_time, pitch in note_values:
        if note in valid_notes:
            if onset_time not in onset_groups:
                onset_groups[onset_time] = []
            onset_groups[onset_time].append(note)

    onset_positions = []
    for onset_time in sorted(onset_groups.keys()):
        notes = onset_groups[onset_time]
        note_positions = map_notes_to_fretboard(notes, standard)
        valid_positions = filter_positions_by_fret_range(note_positions)
        if valid_positions:  # Only append if valid positions exist
            onset_positions.append(valid_positions)

    return onset_positions

def movement_cost(combo, prev_combo):
    """
    Calculate movement cost between two combinations.
    """
    cost = 0
    for cur, prev in zip(combo, prev_combo):
        if cur[1] != 0 and prev[1] != 0:  # Exclude open strings
            cost += abs(cur[1] - prev[1])  # Fret distance
    return cost

def select_best_combination(onset_positions, previous_combination):
    """
    Select the best combination of positions to minimize hand movement.

    Parameters:
    - onset_positions: List of valid combinations for the current onset.
    - previous_combination: Positions selected for the previous onset.

    Returns:
    - best_combination: The combination with the least hand movement.
    """
    if not previous_combination:  # For the first onset
        return onset_positions[0] if onset_positions else []

    # Find the combination with the least movement cost
    best_combination = min(
        onset_positions,
        key=lambda combo: movement_cost(combo, previous_combination),
    )
    return best_combination

def generate_tabs(selected_positions, onset_times, standard, measure_width=20, time_unit=0.1):
    """
    Generate guitar tabs with spacing based on onset times and format them into measures.

    Parameters:
    - selected_positions: List of selected (string, fret) combinations for each onset.
    - onset_times: List of onset times corresponding to the positions.
    - standard: 2D array of guitar strings and frets.
    - measure_width: Number of characters per measure.
    - time_unit: Time represented by each character (default: 0.1 seconds).

    Returns:
    - tab_data: List of strings representing the formatted guitar tabs.
    """
    tabs = [[] for _ in range(6)]  # Initialize 6 strings
    previous_time = 0

    for i, combo in enumerate(selected_positions):
        onset_time = onset_times[i]

        # Calculate spacing based on onset time
        spacing = int(round((onset_time - previous_time) / time_unit))
        previous_time = onset_time

        # Add spacing to all strings
        for line in tabs:
            line.extend(["- "] * spacing)

        # Add notes for this onset
        for string, fret in combo:
            tabs[string][-1] = f"{fret:2} "  # Replace the last dash with the fret number + space

    # Convert each tab line to a string
    tab_data = ["".join(line).rstrip() for line in tabs[::-1]]  # High to low strings
    return tab_data


def save_tabs_to_txt(tab_data, filename="guitar_tabs.txt", measure_width=20):
    """
    Save the generated tabs to a .txt file with three measures per set of lines.

    Parameters:
    - tab_data: List of strings representing the tabs for each string.
    - filename: Name of the output file.
    - measure_width: Number of characters per measure (excluding '|').
    """
    with open(filename, "w") as f:
        strings = ["e|", "B|", "G|", "D|", "A|", "E|"]
        num_measures = (len(tab_data[0]) + measure_width - 1) // measure_width

        for measure_group in range(0, num_measures, 3):  # Process in groups of 3 measures
            for i, line in enumerate(tab_data):
                # Extract three measures and join them with '|'
                measures = [
                    line[measure * measure_width:(measure + 1) * measure_width]
                    for measure in range(measure_group, measure_group + 3)
                ]
                f.write(f"{strings[i]}{'|'.join(measures)}\n")
            # Add a blank line between sets of lines
            f.write("\n")

def main(note_values, standard, output_filename="guitar_tabs.txt"):
    """
    Main function to generate guitar tabs from note values and save them to a .txt file.

    Parameters:
    - note_values: np.array with [note, onset_time, pitch].
    - standard: 2D array for guitar strings and frets.
    - output_filename: Name of the output file for the tabs (default: "guitar_tabs.txt").
    """
    if note_values.size == 0:
        print("No note values provided.")
        return

    print("Processing onsets...")
    onset_positions = process_onsets(note_values, standard)

    if not onset_positions:
        print("No valid positions found for any onset.")
        return

    print("Selecting best combinations...")
    onset_times = sorted(set(note_values[:, 1].astype(float)))
    selected_positions = []
    previous_combination = None

    for positions in onset_positions:
        best_combination = select_best_combination(positions, previous_combination)
        selected_positions.append(best_combination)
        previous_combination = best_combination

    print("Generating tabs...")
    tab_data = generate_tabs(selected_positions, onset_times, standard)

    print(f"Saving tabs to {output_filename}...")
    save_tabs_to_txt(tab_data, filename=output_filename)

    print("Tab generation complete.")
    return tab_data
