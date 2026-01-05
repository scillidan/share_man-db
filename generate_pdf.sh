#!/bin/bash

# Create a directory for PDF files if it doesn't exist
mkdir -p _pdf

# Notify the start of the process
echo "Starting man page to PDF conversion..."

# Get the list of man pages and process each one
man -k . | awk '{print $1}' | sort -u | while IFS= read -r manpage; do
    echo "Processing man page: $manpage"

    # Convert man page to PDF and check for errors
    if man -Tpdf "$manpage" > "_pdf/${manpage}.pdf"; then
        filesize=$(stat -c%s "_pdf/${manpage}.pdf")
        if [ "$filesize" -gt 0 ]; then
            echo "Converted $manpage => ${manpage}.pdf (size: $filesize bytes)"
        else
            echo "WARNING: PDF file has zero size for man page $manpage"
        fi
    else
        echo "Failed to convert $manpage"
    fi
done

# Notify the end of the conversion process
echo "Conversion completed."