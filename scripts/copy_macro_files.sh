#!/bin/bash

# Get the project root directory (parent of the script's directory)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Define target directories relative to the project root
GDS_DIR="$PROJECT_ROOT/openlane/user_project_wrapper/macro/gds"
LIB_DIR="$PROJECT_ROOT/openlane/user_project_wrapper/macro/lib"
LEF_DIR="$PROJECT_ROOT/openlane/user_project_wrapper/macro/lef"

# List of directories to copy from (easily extensible)
SOURCE_DIRS=(
    "S_term_single"
    "S_term_single2"
    "S_term_RAM_IO"
    "S_term_DSP"
    "N_term_single"
    "N_term_single2"
    "N_term_RAM_IO"
    "N_term_DSP"
    "DSP"
    "RAM_IO"
    "RegFile"
    "W_IO"
    "LUT4AB"
    "BRAM"
)

# Ensure script is executed from the project root
if [[ $(pwd) != "$PROJECT_ROOT" ]]; then
    echo "Please run this script from the project root: $PROJECT_ROOT"
    exit 1
fi

# Create target directories if they don't exist
mkdir -p "$GDS_DIR" "$LIB_DIR" "$LEF_DIR"

# Iterate through source directories and copy files
for dir in "${SOURCE_DIRS[@]}"; do
    SRC_PATH="$PROJECT_ROOT/openlane/$dir/runs/$dir/results/signoff"
    if [[ -d "$SRC_PATH" ]]; then
        echo "Processing $dir..."

        # Copy .gds files
        find "$SRC_PATH" -maxdepth 1 -type f -name "*.gds" ! -name "*.*.*" -exec cp -v {} "$GDS_DIR" \;

        # Copy .lib files
        find "$SRC_PATH" -maxdepth 1 -type f -name "*.lib" ! -name "*.*.*" -exec cp -v {} "$LIB_DIR" \;

        # Copy .lef files
        find "$SRC_PATH" -maxdepth 1 -type f -name "*.lef" ! -name "*.*.*" -exec cp -v {} "$LEF_DIR" \;
    else
        echo "Warning: Source path $SRC_PATH does not exist. Skipping..."
    fi
done

echo "File copy operation completed!"
