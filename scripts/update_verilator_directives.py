#!/usr/bin/env python3

import os
import argparse

# List of valid Tilename values
TILE_NAMES = [
    "S_term_single", "S_term_single2", "S_term_RAM_IO", "S_term_DSP",
    "N_term_single", "N_term_single2", "N_term_RAM_IO", "N_term_DSP",
    "DSP", "RAM_IO", "RegFile", "W_IO"
]

# Individual Verilator directives
LINT_OFF_LINES = [
    "/* verilator lint_off UNUSEDSIGNAL */",
    "/* verilator lint_off UNDRIVEN */",
    "/* verilator lint_off UNUSEDPARAM */"
]

LINT_ON_LINES = [
    "/* verilator lint_on UNUSEDSIGNAL */",
    "/* verilator lint_on UNDRIVEN */",
    "/* verilator lint_on UNUSEDPARAM */"
]

def ensure_directives(lines, directives, position):
    """
    Ensures the given directives are present at the specified position.

    Args:
        lines (list): The lines of the file.
        directives (list): List of directives to ensure.
        position (int): Position to insert directives (1 for after the first line, -1 for end).
    """
    if position == 1:
        insertion_index = 1
        range_to_check = lines[:5]  # Check near the start
    else:
        insertion_index = len(lines)
        range_to_check = lines[-5:]  # Check near the end
        if not lines[-1].strip():  # Ensure trailing newline for consistent formatting
            insertion_index -= 1

    # Add missing directives
    for directive in directives:
        if not any(directive in line for line in range_to_check):
            lines.insert(insertion_index, directive + "\n")
            insertion_index += 1

def update_verilog_file(filepath):
    """
    Updates a Verilog file to add Verilator directives if they are missing.

    Args:
        filepath (str): Path to the Verilog file.
    """
    with open(filepath, 'r') as file:
        lines = file.readlines()

    # Ensure Lint-Off directives are present after the first line
    ensure_directives(lines, LINT_OFF_LINES, position=1)

    # Ensure Lint-On directives are present at the end of the file
    ensure_directives(lines, LINT_ON_LINES, position=-1)

    # Write back the updated content
    with open(filepath, 'w') as file:
        file.writelines(lines)

def process_files(base_dir, tile_names):
    """
    Processes Verilog files in the given directory.

    Args:
        base_dir (str): Base directory containing the Verilog files.
        tile_names (list): List of valid tile names.
    """
    for tile_name in tile_names:
        filepath = os.path.join(base_dir, tile_name, f"{tile_name}.v")
        if os.path.exists(filepath):
            print(f"Processing {filepath}...")
            update_verilog_file(filepath)
        else:
            print(f"File not found: {filepath}")

def main():
    parser = argparse.ArgumentParser(description="Add Verilator directives to Verilog files.")
    parser.add_argument(
        "--base-dir", 
        type=str, 
        default="./verilog/rtl/Tile",
        help="Base directory containing the Verilog files."
    )
    args = parser.parse_args()

    process_files(args.base_dir, TILE_NAMES)

if __name__ == "__main__":
    main()
