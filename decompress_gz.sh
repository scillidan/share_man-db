#!/bin/bash

# Directory to search; default to current if not specified
SEARCH_DIR="${1:-.}"

# Temporary directory for extraction under the current directory
TEMP_DIR="./_decompress"

# Create the temporary directory if it doesn't exist
mkdir -p "$TEMP_DIR"

# Find all .gz files recursively and process them
find "$SEARCH_DIR" -type f -name "*.gz" | while IFS= read -r gzfile; do
    echo "Decompressing: $gzfile"

    # Preserve original directory structure
    # Get the directory path relative to SEARCH_DIR
    REL_DIR=$(dirname "${gzfile/#$SEARCH_DIR/}")

    # Create the corresponding directory structure in the TEMP_DIR
    mkdir -p "$TEMP_DIR$REL_DIR"

    # Check if the .gz file is corrupted
    if gunzip -t "$gzfile" 2>/dev/null; then
        # Attempt to decompress the file into TEMP_DIR and remove the original .gz file
        if gunzip -k -c "$gzfile" > "$TEMP_DIR$REL_DIR/$(basename "$gzfile" .gz)"; then
            echo "Successfully extracted $gzfile to $TEMP_DIR$REL_DIR."
            rm -f "$gzfile"  # Remove the original .gz file after successful extraction
        else
            echo "Failed to decompress $gzfile."
        fi
    else
        echo "$gzfile is corrupted."
    fi
done

echo "Decompression process completed."