#!/bin/bash

# Define the target URL and output file
URL="http://sphinx.if.uj.edu.pl/test_data/rootfiles/"
OUTPUT_FILE="file_urls.txt"

# Fetch the directory listing and extract file URLs
curl -s "$URL" | \
grep -oP '(?<=href=")[^"]*' | \
grep -v '/' | \
awk -v prefix="$URL" '{print prefix $1}' > "$OUTPUT_FILE"

echo "File URLs have been saved to $OUTPUT_FILE"

