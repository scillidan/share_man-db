#!/bin/bash

# Directory to search; default to current if not specified
SEARCH_DIR="${1:-.}"

# Find all files in the specified directory and handle spaces in filenames
find "$SEARCH_DIR" -type f -print0 | while IFS= read -r -d '' file; do
    newfile="${file}.txt"
    echo "Renaming '$file' to '$newfile'"

    # Check if newfile already exists to avoid overwriting
    if [ -e "$newfile" ]; then
        echo "Warning: '$newfile' already exists. Skipping."
    else
        if mv "$file" "$newfile"; then
            echo "Successfully renamed '$file' to '$newfile'"
        else
            echo "Error: Failed to rename '$file' to '$newfile'."
        fi
    fi
done

# Summary message after processing
echo "Rename operation completed."