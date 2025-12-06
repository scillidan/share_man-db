#!/bin/bash

# Create a directory for PDF files if it doesn't exist
mkdir -p _pdf

# Log file to keep track of the process
echo "Starting man page to PDF conversion..." > _generate_pdf.log

# Initialize counters for successful and failed conversions
success_count=0
failure_count=0

# Get the list of man pages and process each one
man -k . | awk '{print $1}' | sort -u | while IFS= read -r manpage; do
    # Generate a safe filename by replacing spaces and slashes
    safe_name=$(echo "$manpage" | tr '/ ' '__')

    echo "Processing man page: $manpage" >> _generate_pdf.log

    # Convert man page to PDF and check for errors
    if man -Tpdf "$manpage" > "_pdf/${safe_name}.pdf" 2>>_generate_pdf.log; then
        filesize=$(stat -c%s "_pdf/${safe_name}.pdf")
        if [ "$filesize" -gt 0 ]; then
            echo "Converted $manpage => ${safe_name}.pdf (size: $filesize bytes)" >> _generate_pdf.log
            ((success_count++))  # Increment success counter
        else
            echo "WARNING: PDF file has zero size for man page $manpage" >> _generate_pdf.log
            ((failure_count++))  # Increment failure counter for empty files
        fi
    else
        echo "Failed to convert $manpage" >> _generate_pdf.log
        ((failure_count++))  # Increment failure counter
    fi
done

# Log the results of the conversion process
echo "Conversion completed. Successful: $success_count, Failed: $failure_count" >> _generate_pdf.log