#!/bin/bash

sections=("man1" "man2" "man3" "man4" "man5" "man6" "man7" "man8")

for section in "${sections[@]}"; do
    output_file="${section}.txt"
    echo "Running: code2prompt.exe $section -o $output_file"
    code2prompt.exe "man/$section" -o "$output_file"
done