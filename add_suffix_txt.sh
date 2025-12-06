#!/bin/bash

# Directory to search; default to current if not specified
SEARCH_DIR="${1:-.}"

# Initialize counters
success_count=0
failure_count=0
log_file="_add_suffix_txt.log"

# Clear or create the log file
> "$log_file"

# Find all files in the specified directory
find "$SEARCH_DIR" -type f | while read -r file; do
    newfile="${file}.txt"
    echo "Renaming '$file' to '$newfile'"

    # Check if newfile already exists to avoid overwriting
    if [ -e "$newfile" ]; then
        echo "Warning: '$newfile' already exists. Skipping."
        echo "Skipping rename for '$file' to '$newfile': already exists." >> "$log_file"
        ((failure_count++))
    else
        if mv "$file" "$newfile"; then
            ((success_count++))
        else
            echo "Error: Failed to rename '$file' to '$newfile'." >> "$log_file"
            ((failure_count++))
        fi
    fi
done

# Summary of results
echo "Rename operation completed."
echo "Successful renames: $success_count"
echo "Failed renames: $failure_count"

if [ $failure_count -gt 0 ]; then
    echo "Check '$log_file' for details of failed operations."
fi